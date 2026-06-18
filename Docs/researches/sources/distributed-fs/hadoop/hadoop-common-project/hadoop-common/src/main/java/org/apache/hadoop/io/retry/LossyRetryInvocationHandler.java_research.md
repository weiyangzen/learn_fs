<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/LossyRetryInvocationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/LossyRetryInvocationHandler.java

## Purpose
`LossyRetryInvocationHandler` is a test-only subclass of `RetryInvocationHandler` that simulates lost responses by throwing fake `RetriableException`s for the first N successful underlying method invocations.

## Important APIs and Types
The constructor accepts `numToDrop`, a `FailoverProxyProvider`, and a `RetryPolicy`. It overrides `invoke` to reset a thread-local retry count and `invokeMethod` to drop results until the configured count is reached.

## Control Flow
Each top-level invocation sets `RetryCount` to zero. The underlying method is invoked normally; if the thread-local count is below `numToDrop`, the handler increments it and throws `RetriableException`, causing retry policy handling. Once enough responses have been dropped, it returns the real result.

## State and Persistence
State includes immutable `numToDrop` and a static thread-local counter. No persistent state exists.

## Dependencies and Integration Points
It integrates with retry tests, `RetriableException`, and the superclass retry/failover machinery.

## Risks and Edge Cases
The static thread-local is not cleared after invocation, so long-lived test threads can retain the last integer value. Because it invokes the target before throwing, it simulates lost responses rather than pre-execution failures and can duplicate side effects unless paired with idempotent/at-most-once test methods.

## Test Signals
Tests using this handler should assert exact retry counts, final returned value after drops, behavior when policy retry budget is too small, and no cross-thread interference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/LossyRetryInvocationHandler.java -->
