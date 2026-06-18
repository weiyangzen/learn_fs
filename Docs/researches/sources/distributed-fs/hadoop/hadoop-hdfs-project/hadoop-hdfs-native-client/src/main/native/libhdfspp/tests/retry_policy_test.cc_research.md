# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/retry_policy_test.cc

## Purpose

This unit test validates retry policy decisions for no-retry and fixed-delay retry behavior.

## Important APIs, types, and functions

It tests `NoRetryPolicy`, `FixedDelayRetryPolicy`, `RetryAction`, and `ShouldRetry()`. Status input uses `Status::Unimplemented()`.

## Control flow, state, and persistence

`TestNoRetry` expects immediate `FAIL`. `TestFixedDelay` constructs a policy with delay `100` and max retries `10`, then checks retry decisions below the limit and fail decisions when either retry counter reaches 10. Retry policy state is held in the policy object configuration only.

## Dependencies and integration points

The file depends on `common/retry_policy.h` and gmock. Retry policies are consumed by RPC connection and connect retry flows, especially in `rpc_engine_test.cc`.

## Risks and test signals

The test catches off-by-one retry limit regressions and delay propagation. It does not cover policy differences by status class or idempotency beyond passing `true`, so more specialized retry behavior would need additional cases.
