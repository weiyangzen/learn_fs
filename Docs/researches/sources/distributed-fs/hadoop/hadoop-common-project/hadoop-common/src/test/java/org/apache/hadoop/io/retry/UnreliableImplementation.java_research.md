# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/UnreliableImplementation.java

## Purpose
`UnreliableImplementation` is a deterministic failure fixture for retry and failover tests. It implements `UnreliableInterface` with counters that fail or succeed in predictable sequences.

## Important APIs, Types, and Functions
The class tracks invocation counts for one-time, ten-time, SASL, access-control, and succeed-then-fail methods. `TypeOfExceptionToFailWith` selects `UNRELIABLE_EXCEPTION`, `STANDBY_EXCEPTION`, `IO_EXCEPTION`, or `REMOTE_EXCEPTION`. `throwAppropriateException()` maps that enum to the corresponding checked exception. `setIdentifier()` mutates the identifier used by failover tests.

## Control Flow
Methods either no-op, always throw, throw only until a counter threshold is crossed, or compare an incoming identifier to the instance identifier. Succeed-then-fail methods return the identifier until their success budget is exhausted, then throw the configured exception type.

## State and Persistence
All behavior depends on mutable in-memory counters, `identifier`, and `exceptionToFailWith`. There is no synchronization, persistence, or reset method beyond constructing a new instance.

## Dependencies and Integration Points
It depends on Hadoop `RemoteException`, `StandbyException`, `AccessControlException`, and Java `SaslException`/`IOException`. It is package-private and intended only for retry tests.

## Risks and Edge Cases
The fixture is not thread-safe except where subclasses add coordination. Counter state persists across method calls on the same instance, so tests must create fresh instances or account for prior calls. `failsWithWrappedAccessControlException()` wraps access control two layers deep, matching special unwrapping paths.

## Test Signals
Useful signals are predictable transition after first or tenth invocation, configured exception type and message, identifier comparison behavior, and mutable identifier recovery in failover tests.
