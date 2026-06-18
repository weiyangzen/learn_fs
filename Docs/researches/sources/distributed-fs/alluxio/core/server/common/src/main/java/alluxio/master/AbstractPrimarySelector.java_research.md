# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/AbstractPrimarySelector.java

## Purpose
`AbstractPrimarySelector` supplies synchronization and listener mechanics for implementations that detect whether a master is primary or standby.

## Important APIs, Types, And Functions
Subclasses call protected `setState(NodeState)`. Public APIs implement `getState`, lock-free `getStateUnsafe`, `onStateChange`, and `waitForState`. Listeners are wrapped in unique `AtomicReference` instances and removed through a returned `Scoped`.

## Control Flow, State, Dependencies, Risks, And Tests
State starts as `STANDBY`. `setState` locks, updates state, signals waiters, invokes listeners synchronously, and logs. The state is in-memory coordination state only. Dependencies include `NodeState`, `LockResource`, Java locks/conditions, and `Scoped`. Risks include slow or throwing listeners running inside the state lock, listener set uniqueness based on wrapper identity rather than listener equality, and `getStateUnsafe` observing volatile state without coordinated waits. Tests should verify wait wakeups, listener registration/removal, state ordering, concurrent state transitions, and listener exception behavior.
