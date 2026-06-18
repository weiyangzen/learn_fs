# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/MetricsMasterClientServiceHandler.java

Purpose: gRPC client-facing handler for the metrics master. It exposes clear, heartbeat, and get-metrics RPCs from `MetricsMasterClientServiceGrpc.MetricsMasterClientServiceImplBase` and delegates all behavior to the injected `MetricsMaster`.

Important APIs/types/functions: constructor validates `MetricsMaster`; `clearMetrics` calls `MetricsMaster.clearMetrics`; `metricsHeartbeat` converts nested protobuf client metrics to `alluxio.metrics.Metric` objects and calls `clientHeartbeat(source, metrics)` per source; `getMetrics` returns the master's metric map in `GetMetricsPResponse`.

Control flow: every RPC is wrapped by `RpcUtils.call`, which centralizes logging, exception translation, and stream observer completion. Heartbeat iterates `request.getOptions().getClientMetricsList()`, creates a fresh Java list for each source, converts each protobuf metric through `Metric.fromProto`, then reports the list to the metrics master.

State and persistence: this handler stores only the master reference and is annotated not thread-safe; persistent behavior is delegated to the master and `MetricsStore`. It does not cache or journal client metrics itself.

Dependencies/integration: integrates with generated gRPC request/response types, `RpcUtils`, Guava `Lists`, and the `MetricsMaster` implementation used by the master registry.

Risks: null request internals are not explicitly guarded beyond protobuf defaults. Large heartbeat batches allocate a list per client source. The not-thread-safe annotation is worth respecting because gRPC service implementations are often shared unless guarded upstream.

Test signals: useful tests should verify clear delegation, protobuf-to-`Metric` conversion for multiple client sources, empty heartbeat handling, exception propagation through `RpcUtils`, and `getMetrics` map preservation.
