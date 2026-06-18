# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/retry/TestDefaultRetryPolicy.java

## Purpose
`TestDefaultRetryPolicy` validates the default retry policy's action ordering and its handling of `RetriableException` directly or wrapped in `RemoteException`.

## Important APIs, Types, and Functions
The tests use `RetryPolicy.RetryAction.RetryDecision`, `RetryUtils.getDefaultRetryPolicy()`, `RetriableException`, and `RemoteException`. Assertions use AssertJ to inspect the returned `RetryAction.action`.

## Control Flow
`testRetryDecisionOrdering()` asserts enum ordering from `FAIL` to `RETRY` to `FAILOVER_AND_RETRY`. `testWithRetriable()` and `testWithWrappedRetriable()` construct an enabled default policy with spec `10000,6` and assert retry. `testWithRetriableAndRetryDisabled()` constructs the same spec with the enable flag false and asserts fail.

## State and Persistence
All state is local `Configuration` and policy instances. There is no filesystem or static mutation.

## Dependencies and Integration Points
This file tests retry decisions that are consumed by IPC and client code using Hadoop's default retry policy configuration. It integrates with `RemoteException` class-name unwrapping behavior.

## Risks and Edge Cases
The tests use retry count and failover count zero and idempotent flag true, so they do not cover exhaustion behavior across repeated attempts. They rely on enum ordering as a semantic contract.

## Test Signals
Signals are action ordering consistency, `RETRY` for direct/wrapped retriable exceptions when enabled, and `FAIL` when the default retry policy is disabled.
