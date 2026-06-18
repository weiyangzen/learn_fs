# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/master/AbstractPrimarySelectorTest.java

## Purpose
`AbstractPrimarySelectorTest` verifies primary-selector state reads, blocking waits for state transitions, and listener registration/unregistration.

## Important APIs, Types, and Functions
Tests are `getState()`, `waitFor()`, and `onStateChange()`. The nested `TestSelector` extends `AbstractPrimarySelector` with no-op `start()` and `stop()`. It uses `NodeState`, `Scoped`, scheduled executors, and atomic counters.

## Control Flow, State, and Persistence
`getState()` directly toggles state and verifies safe and unsafe reads. `waitFor()` schedules delayed transitions to primary and standby and blocks until each state is observed. `onStateChange()` registers a listener, performs ten primary/standby cycles, verifies counters, closes the listener, and verifies no further increments. There is no persistence.

## Dependencies and Integration Points
It depends on the abstract master primary selector and JUnit. The behavior is important for master leader-election consumers waiting for primary or standby state.

## Risks and Test Signals
Risks covered include missed notifications, unsafe/safe state mismatch, and listener leaks after close. Passing tests signal basic state coordination but do not exercise concrete selector backends.
