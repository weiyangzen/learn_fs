<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryPolicy.java

## Purpose
`RetryPolicy` defines the decision contract used by retry proxies to decide whether a failed method call should fail, retry, or fail over and retry.

## Important APIs and Types
`RetryAction` carries `RetryDecision action`, `delayMillis`, and optional `reason`. Static actions are `FAIL`, `RETRY`, and `FAILOVER_AND_RETRY`. `RetryDecision` ordering is `FAIL < RETRY < FAILOVER_AND_RETRY`, which is used by multi-exception aggregation.

## Control Flow
Implementations receive the exception, retry count, failover count, and idempotent/at-most-once flag in `shouldRetry`. They return an action or throw an exception to stop retrying.

## State and Persistence
The interface recommends immutable implementations. `RetryAction` is immutable and has no persistence.

## Dependencies and Integration Points
It is consumed by `RetryInvocationHandler`, `RetryPolicies`, `RetryUtils`, and failover providers. It references `Idempotent` and `AtMostOnce` as method-safety inputs.

## Risks and Edge Cases
Policy implementations must keep retry and failover counts semantics straight: retries include failover retries in the caller. Negative delays are not prohibited by `RetryAction` itself, so policies should validate. Throwing from `shouldRetry` bypasses action handling.

## Test Signals
Tests should validate action ordering assumptions, delay propagation, reason logging, implementation immutability, and behavior when policies throw.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryPolicy.java -->
