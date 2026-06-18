# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/TestConnectionRetryPolicy.java

## Purpose
`TestConnectionRetryPolicy` verifies equality and hash-code behavior for connection-level retry policies built by `RetryUtils.getDefaultRetryPolicy()` and for `TryOnceThenFail`.

## Important APIs, Types, and Functions
The helper `getDefaultRetryPolicy(...)` constructs policies from `Configuration`, enable flags, retry specs, and remote exception class names. `verifyRetryPolicyEquivalence()` checks pairwise equality and hash code equality. `newTryOnceThenFail()` exposes a new `RetryPolicies.TryOnceThenFail` instance for equality testing.

## Control Flow
`testDefaultRetryPolicyEquivalence()` builds policies with same and different specs, enabled and disabled modes, and varying `RemoteException` class names. It asserts enabled policies with different specs are unequal, while disabled policies are equal regardless of spec. `testTryOnceThenFailEquivalence()` verifies separate instances compare equal.

## State and Persistence
The test is stateless outside local policy objects and `Configuration` instances. No files or global retry state are persisted.

## Dependencies and Integration Points
It depends on `RetryUtils`, `RetryPolicy`, `RetryPolicies`, Hadoop IPC exception classes, and `PathIOException`. It protects retry policy use in connection-level caching, maps, or comparisons.

## Risks and Edge Cases
The helper accepts a `remoteExceptionToRetry` argument but currently passes an empty string to `RetryUtils`, so remote-exception variation does not influence constructed policies in this test. Equality assertions are sensitive to policy implementation internals.

## Test Signals
Expected signals are stable equality/hash behavior for equivalent policies, inequality when enabled specs differ, and disabled policy equality independent of retry spec.
