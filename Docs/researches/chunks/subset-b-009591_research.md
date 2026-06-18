# sources/user-network-fs/gcsfuse/metrics/otel_metrics.go lines 2599-4417

## Purpose

This chunk is the tail of the generated OpenTelemetry metrics implementation for `gcsfuse`. It finishes the `MetadataCacheReadCount` attribute dispatch, defines the last metric update methods, builds a complete `otelMetrics` instance in `NewOTelMetrics`, and provides shutdown plus observation/logging helpers.

The core purpose is to translate typed metric API calls into low-cardinality OpenTelemetry instruments. Counter-like metrics are stored in per-attribute `atomic.Int64` cells and exported through asynchronous observable callbacks, while histogram values are pushed through a bounded channel to worker goroutines that call OpenTelemetry `Record`.

## High-Level Structure

- Lines 2599-2626: Completes the nested metadata-cache counter switch for `cache_hit=false`, including `EntryStatusNegativeAttr` and `EntryStatusPositiveAttr` by `LookupDetail` value. Unknown enum values are not recorded; they update the sampled unrecognized-attribute state.
- Lines 2628-2636: Implements `ReadBlockSizes`, a histogram recorder for `read/block_sizes`. It enqueues a `histogramRecord` on `o.ch` and silently drops the record if the channel is full.
- Lines 2638-2654: Implements test-only up-down counter methods: one without attributes and one keyed by `RequestTypeAttr1Attr` or `RequestTypeAttr2Attr`.
- Lines 2656-2673: Starts `NewOTelMetrics` by creating the bounded histogram channel, launching sampled logging, starting `workers` goroutines to drain histogram records, and acquiring the `gcsfuse` OpenTelemetry meter.
- Lines 2674-3199: Declares local `atomic.Int64` backing cells for every observable metric/attribute combination used by this constructor: buffered read fallback reasons, file cache read bytes/counts, filesystem op counts, filesystem error category/op matrix, streaming write fallback open mode/reason matrix, GCS read/request/retry metrics, metadata cache combinations, and test up-down counters.
- Lines 3201-3841: Registers 20 OpenTelemetry instruments (`err0` through `err19`): observable counters, histograms, and observable up-down counters. Callback bodies call `conditionallyObserve` for cumulative counters and `observeUpDownCounter` for up-down values.
- Lines 3843-3846: Joins instrument registration errors with `errors.Join`; any registration failure aborts construction.
- Lines 3848-4368: Returns an `otelMetrics` struct wiring the channel, wait group, histogram instruments, and pointers to every local atomic counter. The local atomics escape to heap because the returned struct and OpenTelemetry callbacks hold their addresses.
- Lines 4371-4374: `Close` closes the histogram channel and waits for histogram worker goroutines to finish draining records already accepted into the channel.
- Lines 4376-4417: Helper functions observe nonzero counters, always observe up-down counters, store the first unrecognized attribute value, start periodic sampled logging, and emit a trace log for unknown metric attributes.

## Important APIs And Functions

- `NewOTelMetrics(ctx context.Context, workers int, bufferSize int) (*otelMetrics, error)` is the constructor and integration point. It creates the async histogram worker pool, registers all instruments on `otel.Meter("gcsfuse")`, checks registration errors, and returns the concrete metrics implementation used by callers.
- `ReadBlockSizes(ctx context.Context, value int64)` records read block-size histogram samples. Unlike observable counters, histogram updates are asynchronous and lossy under channel pressure.
- `TestUpdownCounter(inc int64)` and `TestUpdownCounterWithAttrs(inc int64, requestType RequestType)` mutate observable up-down counter backing atomics. The attributed variant rejects unrecognized request types through `updateUnrecognizedAttribute`.
- `Close()` is the lifecycle terminator for histogram workers. After it closes `o.ch`, any later histogram method that sends to `o.ch` can panic, so callers must coordinate shutdown with metric use.
- `conditionallyObserve` exports an observable counter only when its atomic value is greater than zero. This suppresses zero-valued attribute series and limits exported cardinality.
- `observeUpDownCounter` always exports the current value, including zero and negative values, matching up-down counter semantics.
- `updateUnrecognizedAttribute`, `startSampledLogging`, and `logUnrecognizedAttribute` implement sampled diagnostics for enum values that are not in the generated attribute matrix.

## Registered Instruments

This chunk registers the following metric names and kinds:

- Observable counters: `buffered_read/fallback_trigger_count`, `file_cache/read_bytes_count`, `file_cache/read_count`, `fs/ops_count`, `fs/ops_error_count`, `fs/streaming_write_fallback_count`, `gcs/download_bytes_count`, `gcs/read_bytes_count`, `gcs/read_count`, `gcs/reader_count`, `gcs/request_count`, `gcs/retry_count`, and `metadata_cache/read_count`.
- Histograms: `buffered_read/read_latency`, `file_cache/read_latencies`, `fs/ops_latency`, `gcs/request_latencies`, and `read/block_sizes`.
- Observable up-down counters: `test/updown_counter` and `test/updown_counter_with_attrs`.

The latency histograms use explicit buckets. Buffered read, file cache, and filesystem latencies are in microseconds with wide boundaries from tens of microseconds through hundreds of seconds. GCS request latencies are in milliseconds. `read/block_sizes` is in bytes, with boundaries from 0 through 128 MiB.

## Control Flow

1. Metric update methods validate generated enum values with nested `switch` statements. A valid attribute combination adds `inc` to its dedicated atomic counter; an invalid attribute calls `updateUnrecognizedAttribute` and returns without recording.
2. Histogram methods create a `histogramRecord` containing context, instrument, value, and optional attributes, then attempt a nonblocking send to `o.ch`.
3. `NewOTelMetrics` starts a sampled logging goroutine before instrument registration. The logging goroutine exits only when the supplied `ctx` is canceled.
4. `NewOTelMetrics` starts `workers` goroutines that range over the histogram channel. Each worker records with attributes when `record.attributes != nil`; otherwise it records the bare value.
5. The constructor declares all observable counter backing state as local atomics, then registers OpenTelemetry callbacks that close over those local atomics.
6. Each observable counter callback loads every known attribute cell for that metric and calls `obsrv.Observe` only for cells whose value is positive. The up-down callbacks observe unconditionally.
7. The constructor joins all instrument creation errors. On success, it returns an `otelMetrics` whose fields point to the same atomics captured by callbacks; on failure, it returns `nil, err`.
8. `Close` closes the channel and waits for workers to leave their `range` loops after the channel is drained.
9. Sampled logging keeps a single global `unrecognizedAttr` value. The first unknown attribute since the last log tick wins via `CompareAndSwap("", newValue)`, and the ticker swaps it back to empty before logging.

## State And Persistence Behavior

- There is no on-disk persistence. All metric state lives in memory in `atomic.Int64` counters, OpenTelemetry instruments/callback registrations, the histogram channel, worker goroutines, and the global `unrecognizedAttr`.
- Counter state is cumulative for the lifetime of the `otelMetrics` instance. Observable counter callbacks report the current accumulated value rather than deltas; the OpenTelemetry SDK/exporter interprets temporality downstream.
- Histogram records are transient. A record is persisted only long enough to sit in the bounded channel; if the channel is full, the sample is dropped immediately.
- The constructor stores pointers to local atomics in the returned struct. This is intentional escape behavior and lets both update methods and registered callbacks share the same cells.
- `unrecognizedAttr` is package-global. Calling `NewOTelMetrics` resets it to the empty string and starts another sampled logging goroutine, so multiple metrics instances share and overwrite the same unknown-attribute diagnostic slot.
- `Close` drains accepted histogram records but does not unregister OpenTelemetry observable callbacks and does not stop sampled logging. Logging stops through the constructor context, not through `Close`.

## Dependencies And Integration Points

- Depends on `go.opentelemetry.io/otel` for the global meter provider and `go.opentelemetry.io/otel/metric` for instrument creation, callback registration, observation options, histograms, and observers.
- Depends on generated attribute sets defined earlier in the file, such as `fsOpsCountFsOpReadFileAttrSet`, GCS method attr sets, streaming write fallback attr sets, and metadata cache attr sets.
- Depends on enum-like attribute types and constants defined earlier in the generated file, including `RequestType`, `EntryStatus`, `LookupDetail`, read types, GCS methods, filesystem ops, filesystem error categories, open modes, and fallback reasons.
- Integrates with the rest of gcsfuse through the concrete `otelMetrics` methods called by filesystem, cache, GCS, and buffered-read code paths. Those callers do not construct OpenTelemetry options directly; they pass typed attributes to these generated methods.
- Integrates with `internal/logger` only for trace-level reporting of undeclared attributes.
- Uses Go concurrency primitives: `sync.WaitGroup`, `sync/atomic.Int64`, goroutines, and channels.

## Risks And Edge Cases

- Histogram recording is intentionally lossy. `ReadBlockSizes` and other histogram methods using the same channel drop samples when `bufferSize` is exhausted or workers cannot keep up, which can bias latency/size distributions under load.
- `Close` is not idempotent. Calling it twice closes an already closed channel and panics. Calling histogram update methods after `Close` can also panic on send to a closed channel.
- Constructor failure after workers have started can leak goroutines because the error path returns before closing `ch` or waiting on `wg`. Instrument registration errors are probably rare, but tests using a failing meter provider should check this.
- `startSampledLogging` is called before registration succeeds. If construction fails, the logging goroutine still runs until `ctx` is canceled.
- `workers <= 0` is accepted by the `for range workers` loop semantics. With zero workers, histogram sends can fill the buffer and then all future histogram samples are dropped; with a zero buffer and zero workers, all histogram samples are dropped.
- Observable counter callbacks suppress zero values by design. Dashboards or tests expecting an explicit zero time series for every generated attribute combination will not see one until the value becomes positive.
- Up-down counters always observe current values, including zero. This differs from counter observation and is intentional but worth noting for test expectations.
- Unknown attribute diagnostics are sampled and lossy. Only one undeclared value is retained between log ticks, shared globally across all metrics instances and all metric methods.
- The generated filesystem error-count matrix is large. Adding or removing filesystem ops or error categories must keep declarations, callbacks, struct fields, update switches, and returned field wiring synchronized; because this file is generated, changes should flow through the generator.

## Test Signals

- Constructor tests should verify `NewOTelMetrics` returns a non-nil instance with a normal OpenTelemetry meter provider and that `Close` drains worker goroutines without hanging.
- Observable counter tests should increment representative metrics and collect/export observations to confirm only positive counter cells are observed with the expected attribute sets.
- Metadata cache tests should cover valid `cache_hit`, `entry_status`, and `lookup_detail` combinations from the tail switch, plus an invalid value path that triggers sampled unknown-attribute logging rather than incrementing a counter.
- Histogram tests should exercise `ReadBlockSizes` with at least one worker and enough buffer to confirm samples reach the histogram, and with a saturated channel to confirm callers do not block.
- Lifecycle tests should avoid calling `Close` twice or recording histograms after `Close` unless intentionally asserting panic behavior.
- Error-path tests using a custom failing meter provider should check whether workers/logging goroutines remain live after `NewOTelMetrics` returns an error.
- Static regeneration tests should compare generated output against the source metric catalog, especially the 20 registered instruments, explicit bucket boundaries, and the large fs error category by fs op matrix.
