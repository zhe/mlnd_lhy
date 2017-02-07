# coding: utf-8
import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator


class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(
            env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.Q = {}
        self.alpha = 0.1
        self.gamma = 0.09
        self.epsilon = 1
        self.ntrain = 0
        self.allreward = 0
        self.succeed = 0

        self.laststate = None
        self.lastaction = None
        self.lastreward = None

        for s1 in ['forward', 'left', 'right']:  # 目标方向
            for s2 in ['green', 'red']:  # 红绿灯
                for s3 in Environment.valid_actions:
                    for s4 in Environment.valid_actions:
                        self.Q[s1, s2, s3, s4] = {}  # state table
                        for act in Environment.valid_actions:  # action
                            self.Q[s1, s2, s3, s4][act] = 0.0  # action table

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.laststate = None  # 清除上一次的数据
        self.lastaction = None
        self.lastreward = None
        self.ntrain += 1
        self.epsilon = 1.0 / self.ntrain

    def getmaxq(self):
        return max(self.Q[self.state].iteritems(), key=lambda x: x[1])[1]

    def getaction(self):
        if self.getmaxq() == 0:
            return random.choice(self.env.valid_actions)
        if random.random() < self.epsilon:
            return random.choice(self.env.valid_actions)
        else:
            return max(self.Q[self.state].iteritems(), key=lambda x: x[1])[0]

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = (self.next_waypoint, inputs['light'], inputs['oncoming'], inputs['left'])

        # TODO: Select action according to your policy
        # action = random.choice(Environment.valid_actions)
        action = self.getaction()

        # Execute action and get reward
        reward = self.env.act(self, action)
        self.allreward += reward
        if reward == 12 and self.allreward > 0:
            self.succeed += 1
        # if reward < 0:
        #     print self.ntrain, reward

        # TODO: Learn policy based on state, action, reward
        # Q(s,a) = (1-α) * Q(s,a) + α * (R + γ * max (Q(s + 1)))

        if self.laststate:
            self.Q[self.laststate][self.lastaction] = \
                (1 - self.alpha) * self.Q[self.laststate][self.lastaction] + self.alpha * (self.lastreward + self.gamma * self.getmaxq())

        self.lastaction = action
        self.laststate = self.state
        self.lastreward = reward

        # print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""
    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0,
                    display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line

    import numpy as np
    # scores = np.ndarray((11, 11))
    # for alpha in range(11):
    #     for gamma in range(11):
    #         score = 0
    #         for i in range(10):
    #             e = Environment()
    #             a = e.create_agent(LearningAgent)
    #
    #             a.alpha = alpha / 10.0
    #             a.gamma = gamma / 100.0
    #
    #             e.set_primary_agent(a, enforce_deadline=True)
    #             sim = Simulator(e, update_delay=0, display=False)
    #             sim.run(n_trials=100)
    #             score += a.succeed
    #         score /= 10.0
    #         print '{},{},{}'.format(alpha, gamma, score)
    #         scores[alpha, gamma] = score
    #
    # for a in range(11):
    #     for b in range(11):
    #         print str(scores[a, b]) + ',',
    #     print ''

    # print 'epsilon,score'
    # for epsilon in range(10):
    #     score = 0
    #     for i in range(10):
    #         e = Environment()
    #         a = e.create_agent(LearningAgent)
    #
    #         a.epsilon = epsilon / 10.0  # Line 44
    #
    #         e.set_primary_agent(a, enforce_deadline=True)
    #         sim = Simulator(e, update_delay=0, display=False)
    #         sim.run(n_trials=100)
    #         score += a.succeed
    #     score /= 10.0
    #     print '{},{}'.format(epsilon/10.0, score)

if __name__ == '__main__':
    run()
