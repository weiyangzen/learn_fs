<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/AtMostOnce.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/AtMostOnce.java

## Purpose
`AtMostOnce` marks RPC interface methods whose server side guarantees duplicate suppression through a retry cache, allowing clients to retry after failover or uncertain network failures.

## Important APIs and Types
It is a runtime-retained, inherited method annotation targeted at `ElementType.METHOD` and marked `@InterfaceStability.Evolving`.

## Control Flow
`RetryInvocationHandler.ProxyDescriptor.idempotentOrAtMostOnce` reflects on the provider interface method and passes the annotation result to `RetryPolicy.shouldRetry`.

## State and Persistence
The annotation has no fields. Its runtime metadata affects retry behavior but stores no mutable state.

## Dependencies and Integration Points
It is paired with `Idempotent` in retry/failover safety checks and is consumed by `FailoverOnNetworkExceptionRetry` to decide whether socket/IO failures may fail over and retry.

## Risks and Edge Cases
Correctness depends on the server actually maintaining a retry cache and returning prior responses for duplicates. Misannotation can turn uncertain side-effecting calls into repeated operations or, conversely, prevent safe retry if omitted.

## Test Signals
Tests should verify reflection through proxy interfaces, retry policy input flags, duplicate request behavior in servers with retry cache, and failover decisions for methods with and without the annotation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/AtMostOnce.java -->
