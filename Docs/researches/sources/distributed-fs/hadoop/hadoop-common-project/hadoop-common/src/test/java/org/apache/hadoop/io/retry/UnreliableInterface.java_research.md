# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/UnreliableInterface.java

## Purpose
`UnreliableInterface` defines the method surface used by retry and failover tests to simulate controlled transient, fatal, remote, security, and idempotent failures.

## Important APIs, Types, and Functions
Nested `UnreliableException` carries an optional identifier message. `FatalException` extends it for exception-mapping tests. Methods cover always-success, fatal failures, remote fatal failures, one-time IO/remote/unreliable failures, ten-time failures, SASL failures, access-control failures, succeed-then-fail string methods, identifier matching, and non-idempotent void failure.

## Control Flow
The interface itself has no flow, but its method signatures and `@Idempotent` annotations drive `RetryInvocationHandler` decisions in tests. Annotated methods include access-control cases, wrapped access control, idempotent succeed-then-fail, and identifier matching.

## State and Persistence
The interface declares no state. Implementations supply counters and identifiers.

## Dependencies and Integration Points
It depends on `Idempotent`, Hadoop IPC `RemoteException` and `StandbyException`, Hadoop security `AccessControlException`, and Java `SaslException`/`IOException`. It is the core contract used by `TestRetryProxy` and `TestFailoverProxy`.

## Risks and Edge Cases
Comments explicitly note that some annotated methods are not actually idempotent; the annotation is used to test retry decisions. `UnreliableException.getMessage()` returns the identifier and may be null.

## Test Signals
Signals are correct reflection of `@Idempotent` annotations, exception typing in proxy invocation, and method signatures that let retry handlers distinguish safe failover from unsafe retries.
