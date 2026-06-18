# sources/user-network-fs/gcsfuse/metrics/otel_metrics.go lines 1-2598

## Scope

This chunk covers the first 2,598 lines of the generated OpenTelemetry metrics implementation for gcsfuse. The source file is explicitly marked `DO NOT EDIT - FILE IS AUTO-GENERATED`. This range includes imports, precomputed attribute sets, the `histogramRecord` and `otelMetrics` types, most concrete `MetricHandle` recording methods, and the beginning of `MetadataCacheReadCount`. It stops mid-function at the `cacheHit == false` / `EntryStatusNegativeAttr` branch, so constructor setup, callback registration details after line 2,598, helpers, `Close`, and the rest of metadata-cache handling are owned by later chunks.

## Purpose

`otel_metrics.go` is the concrete metrics backend behind `metrics.MetricHandle`. It maps typed metric method calls such as `FsOpsCount`, `GcsRequestCount`, and `FileCacheReadCount` into OpenTelemetry counters and histograms while keeping attribute cardinality fixed to generated enum combinations.

The design in this chunk has two main jobs:

- convert public metric method parameters into predeclared OpenTelemetry attribute sets and per-attribute atomic counters;
- keep hot-path metric recording low overhead by using `atomic.Int64` counters for observable counters and a bounded asynchronous channel for histograms.

## Important Types And Data

The file imports `context`, `errors`, `sync`, `sync/atomic`, `time`, gcsfuse's internal `logger`, and OpenTelemetry packages `otel`, `attribute`, and `metric`.

Key declarations in this chunk:

- `const logInterval = 5 * time.Minute`: cadence for sampled logging of unrecognized attributes, with helper functions outside this range.
- `unrecognizedAttr atomic.Value`: process-global storage for one sampled unknown attribute value.
- many `metric.WithAttributeSet(attribute.NewSet(...))` variables: static attribute options for every supported attribute combination, such as `fs_op=ReadFile`, `gcs_method=NewReader`, `cache_hit=true`, or `read_type=Sequential`.
- `histogramRecord`: carries `ctx`, `metric.Int64Histogram`, numeric value, and optional `metric.RecordOption` for deferred histogram recording.
- `otelMetrics`: concrete implementation state. In this range it contains `ch chan histogramRecord`, a `WaitGroup`, hundreds of pointers to `atomic.Int64` counters, and histogram instruments for buffered-read latency, file-cache latency, filesystem operation latency, GCS request latency, and read block sizes.

The generated field layout mirrors attribute combinations. For example, `fs/ops_error_count` expands into a field for each `FsErrorCategory` and `FsOp` pair, while `metadata_cache/read_count` expands into fields for `cache_hit`, `entry_status`, and `lookup_detail`.

## APIs And Functions

This chunk implements the following `otelMetrics` methods:

- `BufferedReadFallbackTriggerCount(inc, reason)`: increments counts for buffered reader fallback reasons `insufficient_memory` or `random_read_detected`.
- `BufferedReadReadLatency(ctx, latency)`: records buffered-reader read latency in microseconds through the histogram queue.
- `FileCacheReadBytesCount(inc, readType)`: increments file-cache byte counters for `Parallel`, `Random`, `Sequential`, or `Unknown` read types.
- `FileCacheReadCount(inc, cacheHit, readType)`: tracks read request counts split by cache hit boolean and read type.
- `FileCacheReadLatencies(ctx, latency, cacheHit)`: records microsecond file-cache latency with a `cache_hit` attribute.
- `FsOpsCount(inc, fsOp)`: increments total filesystem operation counts for the generated `FsOp` enum values.
- `FsOpsErrorCount(inc, fsErrorCategory, fsOp)`: increments the filesystem error counter for a cross-product of 16 error categories and 25 filesystem operations.
- `FsOpsLatency(ctx, latency, fsOp)`: records filesystem operation latency in microseconds, attributed by operation.
- `FsStreamingWriteFallbackCount(inc, openMode, writeFallbackReason)`: counts streaming-write fallback reasons across five open modes and four fallback reasons.
- `GcsDownloadBytesCount(inc, readType)`: counts downloaded bytes for buffered, parallel, random, and sequential read types.
- `GcsReadBytesCount(inc)`: counts raw GCS read bytes with no attributes.
- `GcsReadCount(inc, readType)`: counts GCS reads for parallel, random, sequential, and unknown read types.
- `GcsReaderCount(inc, ioMethod)`: counts GCS readers opened or closed.
- `GcsRequestCount(inc, gcsMethod)`: counts calls to generated GCS method names including object, folder, appendable-writer, chunk-writer, and multi-range downloader operations.
- `GcsRequestLatencies(ctx, latency, gcsMethod)`: records GCS request latency in milliseconds, attributed by method.
- `GcsRetryCount(inc, retryErrorCategory)`: counts retry categories `OTHER_ERRORS` and `STALLED_READ_REQUEST`.
- start of `MetadataCacheReadCount(inc, cacheHit, entryStatus, lookupDetail)`: validates nonnegative increments and handles the `cacheHit == true` branch plus the start of `cacheHit == false`.

All counter methods in this range reject negative increments by logging an error and returning without mutation. Histogram methods do not check for negative durations in this chunk.

## Control Flow

Counter methods follow a consistent generated pattern:

1. Check `inc < 0`; if true, call `logger.Errorf` with the metric name and return.
2. Switch over each typed attribute argument in a nested order matching the metric schema.
3. On a recognized attribute combination, call `.Add(inc)` on the matching `atomic.Int64`.
4. On an unrecognized enum value, call `updateUnrecognizedAttribute(string(value))` and return without updating a counter.

Histogram methods in this range follow a different pattern:

1. Convert `time.Duration` to the configured integer unit: microseconds for buffered reads, file-cache reads, and filesystem operations; milliseconds for GCS request latencies.
2. Build a `histogramRecord` with the proper histogram instrument and static attribute set.
3. Try to send it to `o.ch` using a nonblocking `select`.
4. Drop the record silently if the channel is full.

`FsOpsErrorCount` is the most expansive visible method. It switches first on `FsErrorCategory` values such as `DEVICE_ERROR`, `DIR_NOT_EMPTY`, `FILE_DIR_ERROR`, `FILE_EXISTS`, `INTERRUPT_ERROR`, `INVALID_ARGUMENT`, `INVALID_OPERATION`, `IO_ERROR`, `MISC_ERROR`, `NETWORK_ERROR`, `NOT_A_DIR`, `NOT_IMPLEMENTED`, `NO_FILE_OR_DIR`, `PERM_ERROR`, `PROCESS_RESOURCE_MGMT_ERROR`, and `TOO_MANY_OPEN_FILES`; each category then switches across the same generated filesystem operation set.

The chunk ends inside `MetadataCacheReadCount`: the visible complete `cacheHit == true` branch handles empty, `negative`, and `positive` `entry_status` values, each split by `found`, `not_found`, and `ttl_expired`. The `cacheHit == false` branch is only partially visible.

## State And Persistence Behavior

The persistent runtime state in this chunk is in-memory only:

- atomic counters accumulate until the `otelMetrics` instance is closed or discarded;
- histograms are buffered in `o.ch` and later recorded by worker goroutines created outside this chunk;
- `unrecognizedAttr` is a global sampled value for unknown attributes and is not persisted beyond process memory.

Observable counters are not updated directly through OpenTelemetry instruments at call time. Instead, these methods mutate atomics; OpenTelemetry callbacks registered in `NewOTelMetrics` later observe nonzero values. The helper `conditionallyObserve` appears after this chunk and explains the nonzero-only observation behavior.

Histogram persistence is intentionally lossy under pressure. If the histogram channel is full, the nonblocking send falls through the `default` branch and the sample is dropped to keep application operations from blocking on metrics.

## Dependencies And Integration Points

Primary local integration points:

- `sources/user-network-fs/gcsfuse/metrics/metric_handle.go`: defines the `MetricHandle` interface and all typed attribute enums consumed by this implementation.
- `sources/user-network-fs/gcsfuse/metrics/noop_metrics.go`: provides the no-op implementation with the same method surface.
- `sources/user-network-fs/gcsfuse/cmd/legacy_main.go`: constructs this backend with `metrics.NewOTelMetrics(ctx, workers, bufferSize)` when metrics are enabled.
- filesystem monitoring wrappers under `internal/fs/wrappers/monitoring.go`: call filesystem operation count, latency, and error methods.
- GCS monitoring under `internal/monitor/bucket.go`: records GCS request latency.
- buffered read and cache readers under `internal/bufferedread` and `internal/gcsx`: record fallback, read count, and cache metrics.

External dependencies are OpenTelemetry's global meter provider and metric API, plus `sync/atomic` for low-contention counters. This generated code assumes the string constants in `metric_handle.go` remain aligned with the generated attribute sets here.

## Risks And Maintenance Notes

The file is generated and highly repetitive. Manual edits are risky because each metric requires coordinated changes across attribute-set declarations, `otelMetrics` fields, constructor initialization/callbacks, record methods, tests, and the public interface.

Important behavioral risks in this chunk:

- unknown attributes are not counted and only one sampled value is retained for logging, so a caller using stale enum strings can lose metric data quietly apart from sampled logs;
- histogram recording is best-effort and can drop samples when `bufferSize` or worker throughput is insufficient;
- counter methods prevent negative increments, but up/down counter methods outside this range intentionally differ;
- durations are converted to integer microseconds or milliseconds, so sub-unit precision is truncated;
- `EntryStatusAttr` is the empty string, which produces attribute sets without `entry_status` in generated metadata-cache counters; this is intentional but easy to misread in tests and dashboards;
- the cross-product expansion for `FsOpsErrorCount` creates a large maintenance surface whenever error categories or filesystem operations change.

Because this chunk stops mid-`MetadataCacheReadCount`, whole-function conclusions need reconciliation with the next chunk.

## Test Signals

`sources/user-network-fs/gcsfuse/metrics/otel_metrics_test.go` provides direct test coverage for this generated implementation using a manual OpenTelemetry reader. The tests create an `otelMetrics` through `NewOTelMetrics`, call methods with specific attribute combinations, collect metrics, and compare encoded attribute/value maps.

Visible test signals relevant to this chunk include:

- table-driven coverage for supported attribute values on `BufferedReadFallbackTriggerCount`, file-cache counters, filesystem operation/error counters, GCS request counters/latencies, retry counters, and metadata-cache read counts;
- negative-increment cases asserting that counters are not decremented or updated by invalid negative values;
- histogram tests that wait briefly for asynchronous processing before collecting manual-reader data;
- metadata-cache tests covering both cache-hit values, empty/negative/positive entry status, and found/not-found/ttl-expired lookup detail combinations.

Integration tests under `internal/fs` and GCS-related packages instantiate `NewOTelMetrics` and exercise the metrics backend through real wrappers, giving additional signal that the generated implementation satisfies the `MetricHandle` contract.
