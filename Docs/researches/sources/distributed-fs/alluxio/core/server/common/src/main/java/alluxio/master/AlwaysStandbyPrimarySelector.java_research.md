# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/AlwaysStandbyPrimarySelector.java

## Purpose
`AlwaysStandbyPrimarySelector` is a trivial primary selector used where a master must never become primary, such as noop/test contexts.

## Important APIs, Types, And Functions
`start` and `stop` do nothing. `getState` and `getStateUnsafe` always return `NodeState.STANDBY`. `onStateChange` returns a no-op unregistration scope. `waitForState` returns immediately for standby and sleeps indefinitely for primary.

## Control Flow, State, Dependencies, Risks, And Tests
There is no mutable state or persistence. Dependencies are `NodeState`, `Scoped`, and `InetSocketAddress`. Risks include `Thread.sleep(Long.MAX_VALUE)` being the primary wait implementation, which relies on interruption for cancellation, and no listener notification ever occurring. Tests should verify standby immediacy, primary wait interruptibility, no-op lifecycle, and no-op listener behavior.
