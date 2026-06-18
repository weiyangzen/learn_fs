<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/Idempotent.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/Idempotent.java

## Purpose
`Idempotent` marks interface methods that can safely be retried because repeated execution has the same effect as one execution.

## Important APIs and Types
It is a runtime-retained, inherited method annotation targeted at methods and classified as evolving.

## Control Flow
`RetryInvocationHandler` reflects this annotation and passes a boolean to `RetryPolicy.shouldRetry`. `FailoverOnNetworkExceptionRetry` uses the boolean to allow failover and retry for socket or uncertain IO failures.

## State and Persistence
The annotation has no elements and no mutable state.

## Dependencies and Integration Points
It is part of the retry package contract with `AtMostOnce`, `RetryPolicy`, and `FailoverProxyProvider`.

## Risks and Edge Cases
Misannotating a non-idempotent method can duplicate side effects. Omitting it can reduce availability because failover policies will fail uncertain network calls instead of retrying.

## Test Signals
Tests should verify runtime retention, inherited behavior on interface methods, interaction with failover-on-network policy, and behavior differences between annotated and unannotated methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/Idempotent.java -->
