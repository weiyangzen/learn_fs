## sources/cloud-native/stargz-snapshotter/fs/metrics/common/metrics.go

Purpose: defines shared Prometheus metrics and log helpers for filesystem operations, including mount latency, registry reads, metadata reads, FUSE node operations, prefetch/background fetch phases, on-demand reads, and byte counters.

Important APIs/types/functions: constants name metric keys and operation labels. Histograms `operationLatencyMilliseconds` and `operationLatencyMicroseconds`, counter `operationCount`, and gauge `bytesCount` are registered once by `Register`. Public helpers are `MeasureLatencyInMilliseconds`, `MeasureLatencyInMicroseconds`, `IncOperationCount`, `AddBytesCount`, `WriteLatencyLogValue`, `WriteLatencyWithBytesLogValue`, and `LogLatencyForLastOnDemandFetch`.

Control flow: callers record a start time, then call measure/log helpers after operations complete. `Register` uses `sync.Once` to set log level and register collectors. Log helpers add fields `metrics`, `operation`, and `layer_sha` to the containerd logger. `LogLatencyForLastOnDemandFetch` only logs positive duration from mount start to last on-demand read.

State and persistence: package-level Prometheus collectors and `logLevel` persist for process lifetime. Metrics are exported through the Prometheus registry; latency logs go to configured logging sinks.

Dependencies and integration points: used by `fs.Mount`, `fs.Check`, `layer.Prefetch`, `layer.BackgroundFetch`, `node.Readdir`, and `file.Read`. `fs.NewFilesystem` calls `Register` unless Prometheus is disabled.

Risks: `Register` only honors the first log level due to `sync.Once`. `bytesCount` is a gauge but helpers only add, so semantics are cumulative unless externally reset. High-cardinality layer digest labels may expand metric series. `LogLatencyForLastOnDemandFetch` silently drops zero/negative durations, which is intentional but can hide missing read-time updates.

Test signals: no direct tests in this subset. Indirect coverage exists where layer/fs paths invoke metrics, but assertions generally do not inspect Prometheus collectors or logs.
