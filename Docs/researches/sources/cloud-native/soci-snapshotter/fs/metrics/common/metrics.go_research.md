# sources/cloud-native/soci-snapshotter/fs/metrics/common/metrics.go

Purpose: defines shared Prometheus metrics and helper functions for SOCI filesystem latency, operation counts, bytes served, image-level counts, and global FUSE failure signaling.

Important APIs and flow: constants name histogram/counter/gauge keys and operation labels such as mount, remote registry GET, metadata init, synchronous read, background fetch, FUSE failures, and background queue size. Package-level Prometheus collectors include millisecond and microsecond latency histograms, operation counters, byte gauges, and image operation gauges. `Register` uses `sync.Once` to register collectors. `MeasureLatencyInMilliseconds`, `MeasureLatencyInMicroseconds`, `IncOperationCount`, `AddBytesCount`, and `AddImageOperationCount` wrap label binding. `ListenForFuseFailure` waits for failure signals and increments `FuseFailureState` at most once per five-minute block. `ReportFuseFailure` increments the operation-specific failure count and sends a nonblocking notification.

State and persistence: all state is process-local Prometheus collector state plus the unbuffered `fuseFailureSignal` channel and `sync.Once`. No filesystem persistence.

Dependencies and integration: used across fs mount, remote HTTP fetch, layer node operations, reader reads, background fetch, and metrics controllers. Registered from `fs.NewFilesystem` unless Prometheus is disabled.

Risks and test signals: metrics with layer/image digest labels can increase cardinality. `AddBytesCount` uses a gauge with additive behavior, which is semantically counter-like but implemented as gauge. `ListenForFuseFailure` blocks during each time block after a signal, intentionally coalescing failures. No tests are present for registration idempotency, label values, or fuse failure coalescing.
