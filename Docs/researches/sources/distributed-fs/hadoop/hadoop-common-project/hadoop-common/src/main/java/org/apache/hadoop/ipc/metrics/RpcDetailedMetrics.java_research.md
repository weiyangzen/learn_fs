<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/RpcDetailedMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/RpcDetailedMetrics.java

## Purpose
`RpcDetailedMetrics` publishes per-RPC-method processing, deferred-processing, and overall request-to-response timing metrics.

## Important APIs, Types, And Functions
- Source name `RpcDetailedActivityForPort<port>`, context `rpcdetailed`.
- `create(int port)` registers with `DefaultMetricsSystem`.
- `init(Class<?> protocol)` initializes rate entries from protocol methods, including `Deferred` and `Overall` prefixes.
- `addProcessingTime`, `addDeferredProcessingTime`, and `addOverallProcessingTime` add samples by RPC call name.
- `shutdown()` unregisters the metrics source.

## Control Flow
`Server` creates this source per listener port and adds samples after calls complete. Deferred calls add both deferred and regular processing metrics when their response is completed.

## State And Persistence
Holds metrics registry/source name and mutable rate aggregators in memory only.

## Dependencies And Integration Points
Used directly by `Server.updateMetrics` and `Server.updateDeferredMetrics`. Depends on metrics2 `MutableRatesWithAggregation`.

## Risks And Edge Cases
Protocol initialization must happen before expected method names are reported. Unknown names can still be added dynamically by the metrics object, but method-level observability may drift. Shutdown is needed to avoid duplicate metrics source registration in tests/restarts.

## Test Signals
RPC tests should assert processing/deferred/overall samples are added with correct names and metrics source unregisters cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/RpcDetailedMetrics.java -->
