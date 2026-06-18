<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/RpcMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/RpcMetrics.java

## Purpose
`RpcMetrics` publishes aggregate server-level IPC metrics: byte counts, queue/processing/response timings, auth outcomes, backoff, slow calls, requeues, successes, connection counts, queue length, and request rate.

## Important APIs, Types, And Functions
- Source name `RpcActivityForPort<port>`, context `rpc`, tagged with port and server name.
- `create(Server, Configuration)` registers the metrics source.
- Time unit defaults to milliseconds and can be configured by `RPC_METRICS_TIME_UNIT`.
- Quantiles are enabled by percentile intervals plus `RPC_METRICS_QUANTILE_ENABLE`.
- Counter incrementers cover authentication, authorization, sent/received bytes, client backoff, disconnected backoff, slow RPCs, requeues, and successful RPC calls.
- Timing adders cover enqueue, queue, lock wait, processing, response, and deferred processing.
- Getter methods expose last-stat processing/deferred sample counts, mean, standard deviation, slow calls, requeues, authorization successes, and tags.

## Control Flow
Construction reads configuration, creates quantile arrays for each configured interval when enabled, and otherwise relies on metrics2-injected mutable counters/rates. `Server` calls byte incrementers from channel IO, timing adders from call completion, and authentication/authorization/backoff counters from handshake and queue paths. Metric methods annotated with `@Metric` pull live values from the associated `Server`.

## State And Persistence
All metrics are in-memory mutable metrics2 objects. No durable state is written. `shutdown()` unregisters the source.

## Dependencies And Integration Points
Tightly integrated with `Server`, `CommonConfigurationKeys`, metrics2 registry/counters/rates/quantiles, and JMX/metrics sinks that consume metrics2 sources.

## Risks And Edge Cases
Invalid time-unit configuration logs and falls back to milliseconds. Quantile arrays are only allocated when enabled; adders guard with `rpcQuantileEnable`. Last-stat mean/stddev depend on metrics snapshot lifecycle and can be zero/empty early. `numOpenConnectionsPerUser()` returns a JSON string from `Server`, so serialization failure appears as null. Duplicate metrics source names can occur if old sources are not unregistered.

## Test Signals
Tests should verify metrics source tags, configured time-unit fallback, quantile creation and updates, counter increments from server events, live server gauge values, slow-RPC/requeue getters, and unregister behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/RpcMetrics.java -->
