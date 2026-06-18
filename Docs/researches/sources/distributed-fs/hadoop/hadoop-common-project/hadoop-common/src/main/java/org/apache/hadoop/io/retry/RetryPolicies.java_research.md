<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryPolicies.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryPolicies.java

## Purpose
`RetryPolicies` is the factory and implementation collection for common Hadoop retry strategies: no retry, retry forever, fixed/proportional/exponential retry limits, exception-dependent retry, remote-exception retry, multiple-linear-random retry, and failover-on-network-exception behavior.

## Important APIs and Types
Public factories include `retryForeverWithFixedSleep`, `retryUpToMaximumCountWithFixedSleep`, `retryUpToMaximumTimeWithFixedSleep`, `retryUpToMaximumCountWithProportionalSleep`, `exponentialBackoffRetry`, `retryByException`, `retryByRemoteException`, `retryOtherThanRemoteAndSaslException`, and `failoverOnNetworkException`. `MultipleLinearRandomRetry` is public with `Pair` and `parseCommaSeparatedString`.

## Control Flow
Simple policies return static fail/retry actions or bounded retry actions with computed delays. `RetryLimited` fails once retry count reaches max and otherwise delegates sleep calculation. `MultipleLinearRandomRetry` maps the current retry number to configured `(numRetries, sleepMillis)` bands and randomizes sleep in `[0.5x, 1.5x]`. Exception-dependent policies select a nested policy by exact exception class or remote exception class name. `FailoverOnNetworkExceptionRetry` first enforces failover/retry limits, fails SASL/token/access-control errors, fails over for connection/standby/observer-active classes, retries retriable exceptions, and only failovers generic socket/IO errors when the method is idempotent or at-most-once.

## State and Persistence
Policies are intended to be immutable. Several cache their string representation lazily. There is no persistent state; runtime randomness comes from `ThreadLocalRandom`.

## Dependencies and Integration Points
It integrates with Hadoop IPC exceptions (`RemoteException`, `RetriableException`, `StandbyException`, `ObserverRetryOnActiveException`), security exceptions (`AccessControlException`, `InvalidToken`, SASL), network exceptions, and `RetryInvocationHandler`.

## Risks and Edge Cases
`RetryUpToMaximumTimeWithFixedSleep` computes max retries as integer division by sleep time; zero sleep time would divide by zero. `calculateExponentialTime` multiplies before capping, so very large `time` and retry values can overflow before `Math.min`. `MultipleLinearRandomRetry.searchPair` uses `curRetry > numRetries`, which makes boundary semantics important. Exception maps use exact classes, not subclasses, except for explicit wrapping helpers. Access-control detection walks causes and can fail if cause chains are malformed.

## Test Signals
Tests should cover policy equality/hash behavior, all retry boundary counts, zero/negative constructor validation, random retry parse failures and valid bands, remote exception class-name matching, SASL/access/token fail-fast behavior, idempotent vs non-idempotent socket handling, exponential cap/overflow cases, and wrapped retriable/access-control exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryPolicies.java -->
