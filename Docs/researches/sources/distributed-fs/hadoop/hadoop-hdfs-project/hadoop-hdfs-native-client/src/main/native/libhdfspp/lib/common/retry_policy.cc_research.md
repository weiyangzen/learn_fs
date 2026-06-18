<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/retry_policy.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/retry_policy.cc

## Purpose
Implements retry policy decisions for RPC communication, including no-retry, fixed-delay retry, and fixed-delay retry with HA failover.

## Important APIs, Types, And Functions
`FixedDelayRetryPolicy::ShouldRetry`, `NoRetryPolicy::ShouldRetry`, and `FixedDelayWithFailover::ShouldRetry` return `RetryAction` values based on status, retry count, failover count, and configured limits.

## Control Flow
No-retry always fails. Fixed-delay retries until total retries plus failovers reaches `max_retries_`. Failover policy triggers failover on timeout or StandbyException while under the failover limit, retries while both retry/failover budgets remain, fails over after local retries are exhausted, and grants one last retry when failover count reaches the max.

## State And Persistence
Policies store delay and retry/failover limits as immutable object state. Counters are supplied by callers; no policy persists progress internally.

## Dependencies And Integration Points
Depends on `Status`, Boost.Asio timeout error codes, and logging. Used by RPC connection and namenode failover loops.

## Risks
`max_failover_conn_retries_` is accepted but not used, so connection-timeout-specific behavior described in comments is incomplete. Idempotency is ignored by all policies. Boundary conditions around `retries <= max_retries_` and final retry/failover can be subtle.

## Test Signals
Tests should table-drive retry/failover decisions for OK/error statuses, timeout, StandbyException, permission/auth failures, exact budget boundaries, delay values, and currently ignored idempotency/max-failover-connection settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/retry_policy.cc -->
