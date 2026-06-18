# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/ControllablePrimarySelector.java

Purpose: test primary selector whose state can be manually changed through inherited `AbstractPrimarySelector` behavior.

Important APIs/types/functions: overrides `start` and `stop` as no-ops; inherits `setState`, `getState`, listeners, and waiting behavior from `AbstractPrimarySelector`.

Control flow: tests instantiate it, call `setState(NodeState.PRIMARY/STANDBY)`, then pass it into master process or context code. Starting/stopping does not contact external election systems.

State and persistence: state is inherited in memory. No persistence.

Dependencies/integration: used by HA-flavored master process tests and emergency backup tests to force primary transitions.

Risks: class comment references `setState(State)` though actual state type is `NodeState` in consumers. Because start does nothing, tests must set initial state explicitly or inherited default behavior may be wrong for the scenario.

Test signals: useful for deterministic promotion/demotion tests, listener tests, and code paths that need primary selector state without real journal election.
