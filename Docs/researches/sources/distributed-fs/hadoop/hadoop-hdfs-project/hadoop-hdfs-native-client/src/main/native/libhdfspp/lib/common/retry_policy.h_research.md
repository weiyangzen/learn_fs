<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/retry_policy.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/retry_policy.h

## Purpose
Declares retry policy types and action values used by libhdfspp RPC and failover logic.

## Important APIs, Types, And Functions
`RetryAction` stores `FAIL`, `RETRY`, or `FAILOVER_AND_RETRY`, a delay, and an optional reason, with static factories and `decision_str()`. `RetryPolicy` is the abstract base. Concrete policies are `FixedDelayWithFailover`, `FixedDelayRetryPolicy`, and `NoRetryPolicy`.

## Control Flow
Callers ask `ShouldRetry` after a failed operation and then either fail, sleep/retry, or switch namenodes and retry.

## State And Persistence
Policy instances store configured delays and limits only. Retry counters remain caller state.

## Dependencies And Integration Points
Included by RPC connection code and configured from `Options` populated by `HdfsConfiguration`.

## Risks
The base default constructor leaves limit fields uninitialized if a subclass used it incorrectly. `decision_str()` includes a defensive default that should be unreachable.

## Test Signals
Compile tests should use polymorphic policy pointers; behavior tests live with `retry_policy.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/retry_policy.h -->
