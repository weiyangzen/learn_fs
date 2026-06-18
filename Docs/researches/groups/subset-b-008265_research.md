# Research Report: subset-b-008265

This grouped report covers the exact subset-b-008265 source list. Each source-file section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/scheduler.rs -->
## sources/object-store/rustfs/crates/io-core/src/scheduler.rs

### Purpose
Implements adaptive I/O scheduling primitives for RustFS `io-core`: priority classification, load-level classification, bandwidth tiering, strategy selection, and buffer-size heuristics. The scheduler decides per-request buffer sizes, readahead enablement, priority, and pressure flags from file size, permit wait time, access style, active request count, and optional storage profile.

### Important APIs, Types, And Functions
`IoPriority` classifies requests as `High`, `Normal`, or `Low` from size thresholds and provides metric-friendly labels. `IoLoadLevel` maps wait duration into `Low`, `Medium`, `High`, or `Critical`. `BandwidthTier` classifies bytes/sec. `IoStrategy` is the decision output: buffer size, flags, current concurrency, optional bandwidth, load, priority, and booleans explaining why buffers were expanded, reduced, or throttled. `IoScheduler` owns `IoSchedulerConfig`, an atomic `active_requests`, and mutex-protected `IoLoadMetrics`. Its main APIs are `calculate_strategy`, `calculate_multi_factor_strategy`, `record_wait_time`, and `load_metrics`. Standalone helpers include `get_concurrency_aware_buffer_size`, `get_advanced_buffer_size`, `get_buffer_size_for_media`, and `calculate_optimal_buffer_size`. `IoSchedulingContext` is a builder-style data carrier for multi-factor scheduling inputs.

### Control Flow
`calculate_strategy` loads active request count, derives priority from file size, derives load from permit wait thresholds, multiplies base buffer size by concurrency, load, and sequential-access factors, clamps by configured min/max, and returns a filled `IoStrategy`. `calculate_multi_factor_strategy` starts from that result and applies storage-media factors, sequential boost, random-access penalty, and profile readahead preference. The standalone helpers layer similarly: file-size short-circuit, basic concurrency adjustment, access-pattern boost/penalty, media adjustment, load multiplier, and final clamping.

### State And Persistence
All state is process-local and in-memory. Active request count is an `AtomicUsize`; load samples are accumulated in a mutex-held `IoLoadMetrics`. There is no persistence across process restarts. `record_wait_time` silently skips updates if the mutex is poisoned or unavailable.

### Dependencies And Integration Points
Uses `IoSchedulerConfig` plus `io_profile::{AccessPattern, StorageMedia, StorageProfile}` from `io-core`. Decision fields and labels are designed to integrate with `rustfs-io-metrics` scheduler metrics, though this file does not emit metrics directly.

### Risks
`IoPriority::from_size` casts `i64` to `usize`, so negative unknown sizes can become huge and classify as low priority. `decrement_requests` uses `fetch_sub` without saturation, so an unbalanced decrement can underflow. The standalone `get_concurrency_aware_buffer_size` hardcodes `concurrent_requests = 1`, which means callers of that helper do not receive real concurrency pressure. The mutex fallback in `load_metrics` can mask poisoned state by returning defaults.

### Test Signals
Unit tests cover priority classification, load classification, bandwidth tiering, scheduler strategy under basic concurrency, load metrics averaging, buffer helpers, media adjustment, optimal sizing, and scheduling-context builder fields.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/scheduler.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/shared_memory.rs -->
## sources/object-store/rustfs/crates/io-core/src/shared_memory.rs

### Purpose
Provides Arc-backed shared data wrappers and a lightweight pool facade for zero-copy-style cross-task sharing. It avoids cloning the underlying payload by wrapping data in `ArcData<T>` and cloning the `Arc`.

### Important APIs, Types, And Functions
`SharedMemoryConfig` configures enablement, maximum pool size, and maximum object size. `SharedMemoryStats` stores atomic totals for created objects, shared references, current memory, and peak memory. `ArcMetadata` records optional size and creation time. `ArcData<T>` wraps `Arc<T>` and metadata, with `new`, `with_size`, `ref_count`, `into_arc`, `metadata`, `size`, `AsRef`, `Deref`, and `Debug`. `SharedMemoryPool` exposes `create`, `create_with_size`, `share`, `stats`, `config`, and `is_enabled`.

### Control Flow
`create` increments `total_objects` and returns `ArcData::new`. `create_with_size` increments object count, adds the supplied size to `current_memory`, updates `peak_memory` if the current total is greater, and returns `ArcData::with_size`. `share` increments `total_shared_refs` and clones the `ArcData`.

### State And Persistence
All state is in atomic counters inside `SharedMemoryPool`; there is no persistent storage. `ArcData` carries metadata for the lifetime of the wrapper. Memory counters are observational and do not own allocation lifecycle.

### Dependencies And Integration Points
Depends only on the standard library (`Arc`, atomics, `Instant`, traits). Intended to integrate with zero-copy readers/writers and metrics paths that need shared ownership without serialization.

### Risks
`SharedMemoryConfig.enabled`, `max_pool_size`, and `max_object_size` are exposed but not enforced by `create` or `create_with_size`. `current_memory` only increases and is never decremented when `ArcData` drops, so it is not an accurate live-memory gauge. Peak update uses load/store rather than CAS, so concurrent creators can race and lose a higher peak. The metadata size is caller-provided and not validated against actual payload size.

### Test Signals
Tests cover `ArcData` creation, clone/reference count behavior, deref access, pool creation/share counters, size metadata, current-memory increment, and default config values.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/shared_memory.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/timeout_wrapper.rs -->
## sources/object-store/rustfs/crates/io-core/src/timeout_wrapper.rs

### Purpose
Defines timeout configuration, per-operation progress tracking, timeout checks, aggregate timeout statistics, and helper functions for adaptive timeout estimation in I/O paths.

### Important APIs, Types, And Functions
`TimeoutConfig` carries base, per-MB, min/max, S3-operation-specific timeouts, and dynamic-timeout enablement. `calculate_timeout` scales base timeout by object size and clamps it. `validate` rejects inconsistent min/max/base relationships. `TimeoutError` distinguishes timeout from invalid configuration. `OperationProgress` tracks total size, processed bytes, last-update time, stale threshold, and start time; it exposes `update`, `add`, `current`, `is_stale`, `progress_percent`, `remaining`, and `transfer_rate`. `RequestTimeoutWrapper` combines config, start time, and optional progress with APIs to check elapsed/remaining/timed-out/stalled state. `TimeoutStats` tracks operation counts, timeout counts, total/max wait time, rate, average wait, and reset. `calculate_adaptive_timeout` and `estimate_bytes_per_second` support external heuristics.

### Control Flow
Dynamic timeout calculation converts bytes to MB, adds `timeout_per_mb * mb` to base, then clamps. Wrapper checks compute the applicable timeout from optional size and compare against elapsed time. Progress updates store or add bytes and refresh last-update time under a mutex. Statistics record operations by atomically adding counts and nanoseconds, with a CAS loop for max wait time. Adaptive timeout starts from historical transfer-rate estimate when available, applies recent-timeout multipliers, then clamps between 5 seconds and 10 minutes.

### State And Persistence
State is process-local. Progress uses atomics plus a mutex-held `Instant`; stats use atomics. There is no external persistence or metrics emission here.

### Dependencies And Integration Points
Uses `thiserror` for `TimeoutError`. Designed for `io-core` request wrappers and can pair with `io-metrics/src/timeout_metrics.rs` for telemetry, though this file does not call metrics macros.

### Risks
`TimeoutStats::avg_wait_time` divides by total operation count using `checked_div`; it safely returns zero for count zero. `OperationProgress::is_stale` returns false on mutex lock failure, which can hide stale work. `update` stores an absolute byte count while `add` increments; misuse can regress or double-count progress. Operation-specific timeout fields are configured but not selected by `RequestTimeoutWrapper`, which only uses base/dynamic size timeout.

### Test Signals
Tests validate timeout calculation and config errors, progress update/add/remaining behavior, wrapper timeout detection with a short sleep, timeout stats rate, and basic progress tracking.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/timeout_wrapper.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/writer.rs -->
## sources/object-store/rustfs/crates/io-core/src/writer.rs

### Purpose
Implements `ZeroCopyObjectWriter`, an in-memory writer optimized around `bytes::BytesMut`/`Bytes` for low-copy object assembly and `tokio::io::AsyncWrite` compatibility.

### Important APIs, Types, And Functions
`ZeroCopyObjectWriter` stores a `BytesMut` buffer, `bytes_written`, and `finalized` flag. Constructors are `new` and `with_capacity`. Write APIs are async `write_zero_copy(Bytes)` and `write_slice(&[u8])`, plus `AsyncWrite::poll_write`. Read/management APIs include `into_bytes`, `as_slice`, `bytes_written`, `capacity`, `len`, `is_empty`, `clear`, and `reserve`. `ZeroCopyWriteError` wraps I/O errors and explicit finalized/invalid-input errors.

### Control Flow
Writes first reject finalized writers, then append data into `BytesMut` and increment `bytes_written`. `into_bytes` consumes the writer, marks it finalized, and freezes the buffer into `Bytes`. The `AsyncWrite` implementation mirrors slice writes and marks finalized on shutdown; flush is a no-op because storage is in memory.

### State And Persistence
All data is held in the process heap until the writer is consumed or cleared. No data is persisted to disk or network. `bytes_written` is reset on `clear`; `finalized` is also reset there.

### Dependencies And Integration Points
Depends on `bytes::{Bytes, BytesMut, BufMut}` and Tokio `AsyncWrite`. Integrates with object write paths needing an in-memory accumulator and with zero-copy metrics in `rustfs-io-metrics`, though no metrics are emitted here.

### Risks
Despite the name, appending a `Bytes` into `BytesMut` via `BufMut::put` may still copy into the mutable buffer; the zero-copy claim depends on bytes crate behavior and source buffer compatibility. The writer is unbounded except by allocation failure; large objects can accumulate whole-object memory. Tests do not directly assert write rejection after `poll_shutdown` on the same writer because `into_bytes` consumes the writer.

### Test Signals
Tokio tests cover construction, `write_zero_copy`, slice writes, conversion to `Bytes`, clear, reserve, multiple writes, `AsyncWriteExt::write`, and debug formatting.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-core/src/writer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/Cargo.toml -->
## sources/object-store/rustfs/crates/io-metrics/Cargo.toml

### Purpose
Defines the `rustfs-io-metrics` crate metadata, benchmark target, dependencies, dev-dependencies, and workspace lint inheritance.

### Important APIs, Types, And Functions
This manifest exposes a library crate named `rustfs-io-metrics` with description "Metrics collection and reporting for RustFS (using metrics crate + OTEL)". It declares a Criterion benchmark named `metrics_pipeline` with `harness = false`.

### Control Flow
There is no runtime control flow. Build-time behavior pulls versions, edition, license, repository, rust-version, and homepage from the workspace. The benchmark target is discovered by Cargo under `benches/metrics_pipeline.rs`.

### State And Persistence
No runtime state. The manifest controls crate identity and dependency graph.

### Dependencies And Integration Points
Runtime dependencies are workspace `metrics`, `rustfs-s3-ops`, `num_cpus`, `thiserror`, `tokio` with `sync,rt`, `tracing`, and `sysinfo`. Dev dependencies add `criterion` and `tokio` with `test-util,rt,macros`. The dependency set maps directly to crate modules: metrics macros, S3 operation labels, CPU-derived cache sharding defaults, error types, async locks/runtime, autotuner logging, and process sampling.

### Risks
The crate says OTEL in metadata but intentionally delegates exporter initialization to `rustfs-obs`; consumers must install a metrics recorder/exporter elsewhere. Tokio features are intentionally narrow; modules using test runtimes rely on dev features. Any new async functionality may need feature expansion.

### Test Signals
The manifest supports regular unit tests and Criterion benchmark execution. The benchmark target is explicitly configured.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/benches/metrics_pipeline.rs -->
## sources/object-store/rustfs/crates/io-metrics/benches/metrics_pipeline.rs

### Purpose
Criterion benchmark suite for measuring hot metrics paths: simple request-start recording, atomic concurrent-request peak updates, and async collector I/O operation recording.

### Important APIs, Types, And Functions
Defines `bench_record_get_object_request_started`, `bench_update_concurrent_requests`, and `bench_metrics_collector_record_io_operation`. Uses `criterion_group!` and `criterion_main!` to expose the benchmark group.

### Control Flow
The first benchmark repeatedly calls `record_get_object_request_started`. The second constructs a `PerformanceMetrics` and repeatedly calls `update_concurrent_requests(64)` through `black_box`. The third builds a current-thread Tokio runtime, creates a `MetricsCollector` with 256 retained latency samples, and repeatedly `block_on`s `record_io_operation(64 KiB, 250 us, read)`.

### State And Persistence
Benchmark state is local to the Criterion process. The metrics recorder, if installed externally, may receive emitted metrics; otherwise metrics macros are effectively no-op depending on global recorder setup.

### Dependencies And Integration Points
Depends on Criterion, Tokio runtime, `PerformanceMetrics`, `MetricsCollector`, and top-level recording helpers. It is integrated through Cargo's `[[bench]]` entry.

### Risks
The collector benchmark includes Tokio `block_on`, lock acquisition, sliding-window insertion, percentile sorting, atomic updates, and metrics macro overhead together, so it is useful for pipeline cost but not isolated micro-cost. The benchmark does not install a recorder, so exporter overhead is excluded.

### Test Signals
Criterion results can reveal regressions in hot recording functions and collector overhead. It complements unit tests by measuring repeated execution cost.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/benches/metrics_pipeline.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/examples/metrics_example.rs -->
## sources/object-store/rustfs/crates/io-metrics/examples/metrics_example.rs

### Purpose
Runnable example demonstrating cache configuration, adaptive TTL, access tracking, unified I/O configuration, and basic metric recording through the `rustfs_io_metrics` public API.

### Important APIs, Types, And Functions
Uses `CacheConfig`, `AdaptiveTTL`, `AccessTracker`, `IoConfig`, `CacheSettings`, `IoSchedulerSettings`, and `record_cache_size`. The example functions are `cache_config_example`, `adaptive_ttl_example`, `access_tracker_example`, `unified_config_example`, and `metrics_recording_example`.

### Control Flow
`main` prints a heading and calls the five example sections. The cache example builds default and custom configs and validates them. The TTL example calculates TTLs for several access counts and checks early eviction. The access tracker simulates hot/warm/cold object accesses and prints counts and classifications. The unified config example composes cache and scheduler settings. The metrics example loops ten times and emits cache-size gauges with hit/miss commentary.

### State And Persistence
All state is local to the example process: in-memory tracker records, config structs, and metrics macro emissions. There is no persistent output beyond stdout and any metrics recorder side effects.

### Dependencies And Integration Points
Documents intended crate usage for downstream RustFS components and human developers. It relies on public re-exports from `lib.rs`.

### Risks
The metrics recording example uses `record_cache_size` as a stand-in for hit/miss activity, which does not actually record cache hits or misses. This can mislead readers unless treated as a simple macro-emission demonstration rather than semantic cache accounting.

### Test Signals
Not a test, but `cargo run --example metrics_example` can validate public API compileability and produce sample output.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/examples/metrics_example.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/adaptive_ttl.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/adaptive_ttl.rs

### Purpose
Provides metric helpers for adaptive TTL behavior plus in-memory access-frequency tracking used by cache TTL decisions.

### Important APIs, Types, And Functions
Recording functions emit TTL adjustment, expiration, early eviction, and access-pattern-change metrics. `AdaptiveTTLStats` is a plain counter summary with adjustment/extension/reduction/expiration/eviction counts and rate helpers. `AccessRecord` tracks count, first/last access, total size, frequency, and idle time. `AccessTracker` maintains a bounded `HashMap<String, AccessRecord>` and exposes `record_access`, count/record lookups, hot/cold checks, `top_keys`, `prune`, `len`, `is_empty`, `clear`, totals, and averages.

### Control Flow
Metric functions call `metrics` macros directly. `AccessTracker::record_access` updates existing records or evicts the oldest record when the map reaches `max_items`, then inserts a new record. `prune` removes records whose last access is outside the configured window. `top_keys` sorts by count descending.

### State And Persistence
`AdaptiveTTLStats` and `AccessTracker` are in-memory only. `AccessTracker` records are local to one tracker instance and are not synchronized internally; callers must provide synchronization if shared across threads.

### Dependencies And Integration Points
Uses `metrics`, `HashMap`, and `Instant`. Integrates with `cache_config::AdaptiveTTL` by providing the access counts and pattern telemetry that TTL decisions can consume.

### Risks
Metric labels `reason`, `from`, and `to` are dynamic strings; unbounded caller-provided values can increase cardinality. `AccessRecord::new` starts count at 1, and `record_access` then increments on existing records, so semantics assume insertion itself is an access. Frequency is computed since first access over the entire record lifetime, not over the configured window unless old records are pruned.

### Test Signals
Tests cover stats rates, metric helper execution, access-record mutation, tracker insertion/update/totals, hot/cold checks, top-key ordering, and clear behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/adaptive_ttl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/autotuner.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/autotuner.rs

### Purpose
Implements an advisory auto-tuner that reads performance metrics, maintains history, and produces tuning recommendations for cache and I/O behavior.

### Important APIs, Types, And Functions
`AutoTuner` owns `Arc<RwLock<TunerConfig>>`, `MetricsHistory`, `Arc<RwLock<TunerState>>`, and an optional `Arc<PerformanceMetrics>`. `TunerConfig` groups `CacheTunerConfig` and `IoTunerConfig`. `TuningResult` describes tuner name, action, previous/new values, and reason. Public APIs are `new`, `with_config`, `with_metrics`, and async `tune`.

### Control Flow
`tune` updates metrics history, reads config, conditionally calls `tune_cache` and `tune_io`, logs any generated recommendations, then updates state with last tune time, count, and results. Cache tuning compares current hit rate to target and threshold. I/O tuning compares average latency to target and threshold. Metrics are read from `PerformanceMetrics` when available, otherwise defaults are used.

### State And Persistence
State is in memory. Config and state are protected by Tokio `RwLock`s. History uses bounded vectors and removes from the front when over capacity. There is no persisted tuning state and no direct mutation of the actual cache or I/O scheduler.

### Dependencies And Integration Points
Depends on `PerformanceMetrics`, Tokio sync, and `tracing`. Integrates with `MetricsCollector`/global metrics only through the shared `PerformanceMetrics` reference.

### Risks
The tuner is currently advisory: it creates `TuningResult`s but does not apply changes to cache size or buffer size. Defaults have both cache and I/O tuning disabled, so `tune` mostly updates state unless enabled. `Vec::remove(0)` is O(n), acceptable for default length 100 but worth noting if enlarged. A missing metrics reference makes cache hit rate 0 and latency 10 ms, which can produce recommendations unrelated to real load.

### Test Signals
Async tests cover creation, tuning with enabled cache config, and bounded metrics-history behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/autotuner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/backpressure_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/backpressure_metrics.rs

### Purpose
Small metrics helper module for backpressure state transitions, request rejections, concurrent operation gauges, and activation/deactivation events.

### Important APIs, Types, And Functions
Exports `record_backpressure_state_change`, `record_backpressure_rejection`, `record_concurrent_operations`, `record_backpressure_activation`, and `record_backpressure_deactivation`.

### Control Flow
Each function is a direct `metrics` macro call. State changes increment a counter labeled by `from` and `to`. Rejections, activations, and deactivations increment counters. Concurrent operation count sets a gauge.

### State And Persistence
The module stores no local state. Persistence and aggregation are delegated to the installed metrics recorder/exporter.

### Dependencies And Integration Points
Integrates with any component enforcing queue or resource backpressure. Re-exported from `lib.rs`.

### Risks
Dynamic `from`/`to` strings can create high-cardinality metrics if callers do not use a constrained state vocabulary. There is no paired state machine here; caller correctness determines whether activation/deactivation counters balance.

### Test Signals
Unit tests execute each recorder to confirm compile-time and runtime macro paths.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/backpressure_metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/bandwidth.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/bandwidth.rs

### Purpose
Maintains a recent bandwidth estimate using an exponential moving average and classifies the estimate into low, medium, high, or unknown tiers.

### Important APIs, Types, And Functions
`BandwidthTier` is a local tier enum. `BandwidthSnapshot` returns current bytes/sec plus tier. `BandwidthMonitor` stores EMA beta, low/high thresholds, and optional current BPS. It exposes `new`, `record_transfer`, `current_bytes_per_second`, `snapshot`, and `tier_for`.

### Control Flow
`new` clamps `ema_beta` to `[0, 1]`. `record_transfer` ignores zero-byte or zero-duration samples, computes sample BPS, and either initializes or updates EMA as `beta * sample + (1 - beta) * current`. `snapshot` converts the optional estimate to zero if absent and classifies via `tier_for`.

### State And Persistence
State is a single in-memory `Option<f64>` inside the monitor. There is no synchronization or persistence.

### Dependencies And Integration Points
Uses only `Duration`. Complements top-level `record_bandwidth` metrics and `io-core` scheduler bandwidth tiering but defines its own `BandwidthTier` type rather than reusing `io-core`.

### Risks
Threshold ordering is not validated; if low threshold exceeds high threshold, tier classification can be surprising. With `ema_beta = 0`, the first sample sticks forever; with `ema_beta = 1`, only the latest sample matters. `snapshot` reports absent bandwidth as `0` and `Unknown`, so callers must distinguish unknown from measured zero only through tier.

### Test Signals
Unit test verifies EMA update from 1000 to 600 BPS with beta 0.5 and resulting medium tier.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/bandwidth.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/cache_config.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/cache_config.rs

### Purpose
Defines cache configuration, adaptive TTL calculation, cache statistics, and cache health classification for object caching.

### Important APIs, Types, And Functions
`CacheConfig` contains capacity, TTL range, memory limit, shard count, adaptive TTL flag, and hot/cold TTL factors. It supports `validate`, duration accessors, and builder methods. `CacheConfigError` reports invalid values. `AdaptiveTTL` stores config, hot/cold thresholds, and access window, with `calculate_ttl`, `should_evict_early`, and `calculate_priority`. `CacheStats` tracks hits, misses, entries, memory, evictions, TTL expirations, and hit/miss rates. `CacheHealthStatus` maps hit rate to healthy/degraded/unhealthy/unknown.

### Control Flow
Validation rejects zero capacity, invalid TTL ordering, default TTL outside range, and invalid extension/reduction factors. TTL calculation optionally extends hot items, reduces cold items, applies hit-rate-based adjustment, and clamps to configured min/max. Early eviction returns true for cold items older than half their current TTL. Priority combines access frequency, recency, and inverse size.

### State And Persistence
All structs are in-memory value types. `CacheStats` is mutable but not atomic; synchronization is caller-owned.

### Dependencies And Integration Points
Uses `num_cpus::get()` for default shard count and `Duration` for TTL. Re-exported from `lib.rs` and demonstrated in the example. Works with `adaptive_ttl::AccessTracker` and cache metrics helpers.

### Risks
`CacheHealthStatus::from_hit_rate` treats any non-negative value below 0.5 as unhealthy and only negative as unknown; values greater than 1.0 become healthy. `should_evict_early` ignores recency beyond age and access count. Priority can heavily penalize large objects, which may be intended but can evict valuable large hot data. Config validation does not check max memory or shard count.

### Test Signals
Tests cover defaults, validation failures, hot/cold TTL adjustment, cache stat rates, health mapping, early eviction, and priority ordering.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/cache_config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/capacity_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/capacity_metrics.rs

### Purpose
Centralizes metrics emission for capacity cache, capacity refresh, scan, timeout fallback, symlink, and dirty-disk behavior.

### Important APIs, Types, And Functions
Exports recorders for cache hit/miss/served, current capacity bytes, update completion/failure, refresh requests/joiners/inflight/results/scope, dirty disk count, write operations, symlink sizes, timeout fallback/stall/dynamic timeout, scan sampling, scan mode, and per-disk scan statistics.

### Control Flow
Each function emits counters, gauges, and/or histograms with labels such as source, mode, result, scope, disk, and estimated. `record_capacity_update_completed` records completion count, duration, bytes, and estimated flag. `record_capacity_scan_disk` emits multiple per-disk histograms and optionally increments partial-error counter.

### State And Persistence
No local state. Aggregation is external through the metrics recorder.

### Dependencies And Integration Points
Uses `metrics::{counter,gauge,histogram}` and `Duration`. Intended for storage-capacity management code that caches disk usage, refreshes capacity, and scans filesystem contents.

### Risks
The `disk` label is caller-provided and can be high cardinality if it includes unstable paths, UUIDs, or transient mount names. Several labels are `&'static str`, which encourages bounded vocabularies for source/mode/result/scope. Histograms for bytes and file counts can be high-volume during large scans.

### Test Signals
No unit tests in this file. Compile coverage comes from crate tests that use exported functions elsewhere, but these specific helpers are not individually asserted here.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/capacity_metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/collector.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/collector.rs

### Purpose
Provides an async `MetricsCollector` that updates `PerformanceMetrics`, records transfer metrics, and computes latency average/P95/P99 over a bounded sliding window.

### Important APIs, Types, And Functions
`MetricsCollector` stores an `Arc<PerformanceMetrics>`, a Tokio `RwLock<VecDeque<Duration>>` of latency samples, and `max_latency_samples`. Public APIs are `new`, `with_default_max_samples`, async `record_io_operation`, async `sample_count`, and `max_samples`.

### Control Flow
`record_io_operation` updates bytes and operation counters based on `is_read`, emits `record_data_transfer`, pushes duration into the sample window, pops the oldest sample if over limit, then calls `update_latency_percentiles`. Percentile update reads samples, copies microsecond values into a vector, sorts it, computes arithmetic average as the "avg" latency, stores avg/P95/P99 into `PerformanceMetrics`, and emits corresponding top-level metrics.

### State And Persistence
Latency samples are in-memory and bounded. Underlying counters are atomics in `PerformanceMetrics`. No persistence exists across process restarts.

### Dependencies And Integration Points
Depends on `PerformanceMetrics`, Tokio `RwLock`, `VecDeque`, and top-level metric functions in `lib.rs`. It is used by benchmarks and global metrics tests.

### Risks
Every recorded operation sorts the entire retained window, which is O(n log n) and may be expensive on hot paths with large windows. P95/P99 index calculation uses `len * percentile` floored and then clamped, which is simple but not a statistically nuanced quantile estimator. `duration.as_millis() as f64` can record `0` for sub-millisecond transfers in `record_data_transfer`, suppressing transfer bandwidth calculation.

### Test Signals
Async tests cover construction, read/write counter updates, sample count, average/P95/P99 updates, sample retention limit, and read/write distinction.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/collector.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/config.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/config.rs

### Purpose
Defines a unified, crate-local configuration surface for cache, I/O scheduler, backpressure, timeout, and deadlock-detection settings.

### Important APIs, Types, And Functions
Constants define default cache capacity/TTL/memory, scheduler concurrency/priority thresholds/buffer bounds, backpressure watermarks, lock timeout, deadlock interval, and buffer sizes. `CacheSettings`, `IoSchedulerSettings`, `BackpressureSettings`, `TimeoutSettings`, `DeadlockDetectionSettings`, and `IoConfig` provide defaults and builder methods. Behavior helpers include backpressure `high_threshold`/`low_threshold` and timeout `timeout_with_backoff`.

### Control Flow
Defaults assemble the configuration graph. Builder methods consume and return modified structs. Backpressure thresholds multiply max capacity by watermark percentages. Retry timeout multiplies default timeout by `retry_backoff_factor.powi(retry_count)`.

### State And Persistence
Configuration is plain in-memory data. There is no config file parsing or persistence.

### Dependencies And Integration Points
Uses `Duration`. Publicly re-exported from `lib.rs`. Overlaps conceptually with `io-core::config::IoSchedulerConfig` and `cache_config::CacheConfig`, making it a high-level metrics crate configuration facade rather than the only runtime config source.

### Risks
There is no validation for watermarks ordering, buffer min/base/max ordering, retry factor bounds, or zero concurrency. Because these settings duplicate ideas from other modules, drift can occur between `IoSchedulerSettings`, `CacheSettings`, and runtime config types. `timeout_with_backoff` can grow very large for high retry counts.

### Test Signals
Tests cover cache and scheduler builders, backpressure threshold math, retry backoff for first and second retry, and unified config composition.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/deadlock_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/deadlock_metrics.rs

### Purpose
Records metrics related to potential deadlocks, long-held locks, lock acquisition/release/contention, and wait-graph edge changes.

### Important APIs, Types, And Functions
Exports `record_deadlock_detected`, `record_long_held_lock`, `record_lock_acquisition`, `record_lock_release`, `record_lock_contention`, `record_wait_edge_added`, and `record_wait_edge_removed`.

### Control Flow
Functions emit counters and histograms through `metrics`. Deadlock detection records total and cycle length. Long-held lock records count and hold duration, ignoring the lock id parameter. Lock acquisition/release/contention record by caller-supplied lock type. Wait-edge helpers increment add/remove counters.

### State And Persistence
No local state. External metrics backend owns retention and aggregation.

### Dependencies And Integration Points
Designed for lock tracking and deadlock detection components. Re-exported from `lib.rs`, while `config.rs` defines deadlock detection settings.

### Risks
`record_long_held_lock` accepts but ignores `_lock_id`, so per-lock diagnosis must happen elsewhere. Dynamic `lock_type` labels can be high cardinality if not constrained. The module records observations only; it does not detect deadlocks or maintain a wait graph.

### Test Signals
Tests execute all recording functions for representative values.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/deadlock_metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/global_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/global_metrics.rs

### Purpose
Provides a singleton `Arc<PerformanceMetrics>` for process-wide shared performance counters.

### Important APIs, Types, And Functions
`GLOBAL_PERFORMANCE_METRICS` is a `OnceLock<Arc<PerformanceMetrics>>`. `get_global_metrics` initializes it with `PerformanceMetrics::new()` on first access and returns a cloned `Arc`.

### Control Flow
Callers invoke `get_global_metrics`; `OnceLock::get_or_init` lazily creates the singleton, and `clone` increments the `Arc` reference count.

### State And Persistence
State is global and process-local. Counter values persist for the lifetime of the process and cannot be reset through this module's public API.

### Dependencies And Integration Points
Depends on `PerformanceMetrics`, `Arc`, and `OnceLock`. Integrates with any component that needs shared counters without passing a metrics object explicitly, and with `MetricsCollector` for global collection.

### Risks
Global mutable metric state can make tests order-dependent. The tests assert lower bounds after prior writes for some counters, acknowledging cross-test persistence. No reset API exists outside direct access to atomic fields.

### Test Signals
Tests verify pointer identity across calls, recording visibility through the singleton, and collector updates through one `Arc` being visible through another.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/global_metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/internode_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/internode_metrics.rs

### Purpose
Tracks internode network and erasure-write quorum metrics, including aggregate atomic snapshots and labeled operation/backend/classification metrics.

### Important APIs, Types, And Functions
Constants define operation labels (`read_file_stream`, `put_file_stream`, `walk_dir`, gRPC read/write) and backend labels (`tcp-http`, `grpc`, `unknown`). `InternodeOperationMetricDescriptor` and `INTERNODE_OPERATION_METRICS` list expected metric names and label sets. `InternodeMetricsSnapshot` is a readout struct. `InternodeMetrics` stores atomic totals for sent/received bytes, incoming/outgoing requests, errors, dial errors, dial timing, samples, and last dial timestamp. Methods record aggregate and operation/backend-specific bytes, requests, errors, classified errors, retries, retry successes, quorum failures, dial results, snapshots, and test reset. `global_internode_metrics` returns a `LazyLock<Arc<InternodeMetrics>>`.

### Control Flow
Operation-specific methods first update aggregate counters where appropriate, then emit labeled counters. Zero-byte sent/received samples are ignored after aggregate helper checks. Dial results update total time, sample count, average-time gauge, optional error counter, and last dial Unix millis. Snapshot loads atomics and computes average dial time with checked division.

### State And Persistence
State is in process-local atomics; global instance persists for process lifetime. Metrics macro emissions are handled by the configured recorder/exporter.

### Dependencies And Integration Points
Uses `metrics`, `Arc`, `LazyLock`, atomics, `Duration`, and `SystemTime`. It is intended for internode transport layers and erasure-write paths.

### Risks
Classified error/retry/quorum methods emit counters but do not update aggregate snapshot error or retry fields, so snapshots are intentionally limited. Label constants help cardinality, but classification/stage/dominant error must remain bounded. Dial average uses relaxed atomics and a load after increment, which is acceptable for telemetry but not a transactional statistic.

### Test Signals
Tests verify snapshot values after aggregate updates, operation methods updating aggregate snapshots, metric descriptor label sets and stable names, low-cardinality constants, and classified/retry methods not affecting aggregate byte/request snapshot fields.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/internode_metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/io_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/io_metrics.rs

### Purpose
Provides focused metrics helpers and a small in-memory summary struct for I/O scheduler decisions, priorities, load changes, bandwidth observations, buffer adjustments, queue operations, and starvation.

### Important APIs, Types, And Functions
Exports `record_io_scheduler_decision`, `record_io_priority_decision`, `record_load_level_change`, `record_bandwidth_observation`, `record_buffer_size_adjustment`, `record_queue_operation`, `record_starvation_event`, and `IoSchedulerStats`.

### Control Flow
Recording functions emit counters, gauges, and histograms with labels for load level, strategy, priority, reason, operation, and queue priority. `IoSchedulerStats` has mutating methods that increment local counters and `reset`.

### State And Persistence
Metric helper functions store no state. `IoSchedulerStats` is a plain mutable summary; it is not atomic or synchronized and persists only as long as the caller retains it.

### Dependencies And Integration Points
Used by `lib.rs` re-exports and intended to pair with `io-core/src/scheduler.rs` decision outputs. Metrics names are specific to scheduler telemetry.

### Risks
Dynamic label strings can cause high-cardinality series if callers pass unconstrained reasons or priorities. There is overlap with top-level `lib.rs` functions like `record_io_strategy`, `record_io_load_level`, and `record_permit_wait`, so consumers need a consistent naming plan.

### Test Signals
Tests execute each recorder and validate `IoSchedulerStats` counter increments.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/io_metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/lib.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/lib.rs

### Purpose
Acts as the public facade and metric-name implementation hub for `rustfs-io-metrics`. It re-exports submodules and defines many top-level `record_*` functions for S3 operations, zero-copy, bytes pools, scheduling, bandwidth, memory, disk I/O, errors, timeouts, retries, and tracked in-flight memory.

### Important APIs, Types, And Functions
Public modules include adaptive TTL, autotuner, backpressure, cache config, capacity, collector, config, deadlock, internode, I/O metrics, lock metrics, performance, process lock metrics, S3 API metrics, sampler, system path, timeout metrics, bandwidth, global metrics, and metric names. Re-exports expose core types and helpers. Internal statics `EC_ENCODE_INFLIGHT_BYTES` and `GET_OBJECT_BUFFERED_BYTES` back `add/remove/current_ec_encode_inflight_bytes` and `track/current_get_object_buffered_bytes`. `MemoryGaugeGuard` decrements a tracked gauge on drop. Top-level recorders cover GetObject lifecycle, zero-copy read/write/fallback/saved bytes, bytes pool activity, S3 get/put/list/delete, I/O strategy/load/permit wait, cache size, bandwidth/data transfer, memory split/cgroup, CPU/disk, errors/timeouts/retries, I/O latency, and zero-copy extension metrics.

### Control Flow
Most public functions are direct `metrics` macro calls. Memory tracking functions update atomics and set gauges; decrement uses a CAS-based saturating subtraction. `track_get_object_buffered_bytes` returns `None` for zero bytes or a `MemoryGaugeGuard` that decrements on drop. `record_data_transfer` computes bandwidth only if duration is positive. `record_bandwidth` records both an `"all"` tier gauge and a tier-specific gauge.

### State And Persistence
Local persistent state consists of two process-wide atomics for current in-flight byte gauges. Everything else is emitted to the configured metrics recorder. Drop guards provide scoped state cleanup for GET buffering.

### Dependencies And Integration Points
Imports metrics macros globally. Integrates with all submodules via re-exports and with `rustfs-obs` for OTEL exporter setup, per crate docs. It is the main downstream API surface.

### Risks
The file contains overlapping metric helpers with submodules, which can fragment naming if callers mix equivalent functions. Many labels accept `String` from arbitrary `&str` values, so cardinality discipline is caller-owned. `MemoryGaugeGuard` is not cloneable, which is good for ownership, but manual construction is possible inside tests only because fields are private. Metrics emission does not validate values; negative sizes cast to f64 can be recorded in some S3 paths when passed as `i64`, though most functions guard size > 0 before histograms.

### Test Signals
Unit tests execute top-level recording helpers, EC in-flight saturation, GET buffered-byte drop guard behavior, memory/cgroup recording, disk/error/timeout/retry helpers, and zero-copy metric constants/functions.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/lock_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/lock_metrics.rs

### Purpose
Emits metrics for lock optimization, spin behavior, lock hold/contention, early release, and object namespace lock diagnostics.

### Important APIs, Types, And Functions
Exports `record_lock_optimization_enabled`, `record_spin_attempt`, `record_spin_count_change`, `record_lock_hold_time`, `record_early_release`, `record_contention_event`, `record_object_lock_diag_enabled`, `record_object_lock_diag_acquire_duration`, `record_object_lock_diag_hold_duration`, `record_object_lock_diag_slow_acquire`, and `record_object_lock_diag_slow_hold`. `LockMetricsSummary` stores acquisition/release/spin/early/contention counts and computes spin success and contention rates.

### Control Flow
Simple lock metrics emit gauges, counters, or histograms. Object lock diagnostic helpers use static `op` and `mode` labels for acquire/hold duration and slow-event counters. Summary methods compute rates defensively returning zero for empty denominators.

### State And Persistence
No local recorder state. `LockMetricsSummary` is caller-owned in-memory data.

### Dependencies And Integration Points
Uses `metrics` and `Duration`. Re-exported by `lib.rs`, and likely used by namespace lock and lock optimization code.

### Risks
Generic `record_contention_event` and deadlock module `record_lock_contention` use related names but different label behavior, which can confuse dashboards. Object diagnostic labels are `&'static str`, which is good for cardinality if call sites use constants. Summary does not update from recorder functions automatically.

### Test Signals
Tests execute all helpers. Several tests install a local recorder to verify object lock diagnostic gauge, histograms, and counters are registered with expected names. Summary rate calculations are validated.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/lock_metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/metric_names.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/metric_names.rs

### Purpose
Provides stable metric-name constants for zero-copy-related telemetry.

### Important APIs, Types, And Functions
The `zero_copy` module defines constants for buffer operation totals/bytes, memory copy totals/bytes, shared reference operations, BufReader layers eliminated and buffer sizes, Direct I/O operations/bytes, average copy count, throughput MB/s, and current memory saved bytes.

### Control Flow
No runtime control flow. Constants are referenced by `lib.rs` zero-copy extension functions.

### State And Persistence
No state.

### Dependencies And Integration Points
Used by top-level `record_zero_copy_buffer_operation`, `record_memory_copy`, `record_shared_ref_operation`, `record_bufreader_optimization`, `record_direct_io_operation`, and `update_zero_copy_performance_metrics`.

### Risks
Only zero-copy names are centralized here; many other metric names remain inline across modules. Renaming constants would affect dashboards. No compile-time relationship exists between these constants and external metric descriptors.

### Test Signals
`lib.rs` zero-copy tests assert selected constants are non-empty.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/metric_names.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/performance.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/performance.rs

### Purpose
Defines `PerformanceMetrics`, a thread-safe atomic counter bundle for cache, I/O, concurrency, latency, and error counters.

### Important APIs, Types, And Functions
Fields include cache hits/misses/L1/L2, bytes read/written, disk read/write counts, average/P95/P99 latency in microseconds, current/peak concurrent requests, total errors, timeout errors, and disk errors. Methods include `new`, `cache_hit_rate`, `l1_hit_rate`, cache recorders, byte/disk recorders, `update_concurrent_requests`, and error recorders. `Default` delegates to `new`.

### Control Flow
Recording methods perform relaxed atomic increments or stores. L1/L2 hit methods increment tier-specific counter and total hit. `update_concurrent_requests` stores current count and uses a CAS loop to update peak only when the new count exceeds prior peak. Timeout and disk error methods increment specific counters and total error.

### State And Persistence
All state is process-local atomics in the struct. There is no reset method and no persistence. Cloning is not implemented; sharing is expected through `Arc<PerformanceMetrics>`.

### Dependencies And Integration Points
Used by `MetricsCollector`, `AutoTuner`, `global_metrics`, benchmarks, and public API consumers. It is the advanced in-process counterpart to metrics macro emission.

### Risks
Relaxed atomics are appropriate for telemetry but not for strict ordering. Rates can be transiently inconsistent under concurrent updates. No saturation guards exist for counters, though `u64` overflow is unlikely in normal operation. L1 hit rate divides L1 hits by total hits, not total cache lookups.

### Test Signals
Tests cover zero initialization, cache hit rate, L1 hit rate, I/O byte/count recording, concurrent current/peak tracking, and timeout/disk error totals.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/performance.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/process_lock_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/process_lock_metrics.rs

### Purpose
Tracks process-held read/write lock counts and collects platform-specific process I/O and virtual memory counters.

### Important APIs, Types, And Functions
Static atomics `READ_LOCKS_HELD` and `WRITE_LOCKS_HELD` back lock count recorders. `ProcessLockSnapshot` reports current held locks. `ProcessPlatformSnapshot` reports optional I/O character/read/write bytes, syscall read/write totals, and peak virtual memory. Public APIs include acquire/release recorders, `snapshot_process_lock_counts`, and `snapshot_process_platform_stats`. Platform modules implement `snapshot` for Linux (`/proc/self/io` and `/proc/self/status`), Windows (PowerShell CIM), macOS/BSD (`ps`), and fallback unsupported targets.

### Control Flow
Acquire increments atomics. Release uses `fetch_update` with saturating subtraction to avoid underflow. Platform snapshot reads OS data and parses known fields into optional counters. Linux parsing extracts `rchar`, `wchar`, `syscr`, `syscw`, `read_bytes`, `write_bytes`, and `VmPeak`.

### State And Persistence
Held-lock counters are process-wide atomics and persist for the process lifetime or until test reset. Platform snapshots are instantaneous reads; nothing is persisted.

### Dependencies And Integration Points
Feeds `sampler/process.rs`, which combines lock counts with sysinfo process metrics. Re-exported from `lib.rs`.

### Risks
Lock counters depend on balanced acquire/release instrumentation by callers. Release saturation hides double-release bugs in metrics. Non-Linux platforms rely on external commands and may return default/partial snapshots. Parser functions ignore malformed lines and missing fields, which is resilient but can mask platform drift.

### Test Signals
Tests cover held-lock acquire/release saturation and parser helpers. Platform-specific Linux/macOS parser tests validate expected extraction.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/process_lock_metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/s3_api_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/s3_api_metrics.rs

### Purpose
Records generic S3 API operation counts by operation and bucket and provides one-time metric description registration.

### Important APIs, Types, And Functions
`S3_OPS_METRIC` is `rustfs_s3_operations_total`. `record_s3_op` accepts `rustfs_s3_ops::S3Operation` and bucket name. `init_s3_metrics` uses `OnceLock<()>` to call `describe_counter!` only once.

### Control Flow
`record_s3_op` emits a counter labeled by `op.as_str()` and owned bucket string. `init_s3_metrics` lazily registers the counter description through `OnceLock::get_or_init`.

### State And Persistence
Only the `OnceLock` tracks whether the description was initialized in the current process. Metric counts are external to the module.

### Dependencies And Integration Points
Depends on `rustfs-s3-ops` for stable operation labels and on metrics macros imported at crate root. Re-exported from `lib.rs`.

### Risks
Bucket label cardinality can be very high in multi-tenant deployments. This may be acceptable for some observability backends but should be deliberate. There are no local tests in this file.

### Test Signals
No unit tests in the file. Compile coverage comes from crate build and any callers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/s3_api_metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/sampler/mod.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/sampler/mod.rs

### Purpose
Defines the sampler module surface and re-exports process and platform snapshot APIs.

### Important APIs, Types, And Functions
Declares `pub mod process` and `pub mod system`. Re-exports `ProcessResourceSnapshot`, `ProcessStatusSnapshot`, `ProcessSystemSnapshot`, `snapshot_process_resource`, `snapshot_process_resource_and_system`, `snapshot_process_system`, and `snapshot_process_platform`.

### Control Flow
No runtime control flow beyond module wiring and re-export resolution.

### State And Persistence
No state in this module; state resides in `process.rs` and `process_lock_metrics.rs`.

### Dependencies And Integration Points
Serves as the public sampler namespace and is re-exported from `lib.rs`.

### Risks
Because it re-exports both process-level and platform-level snapshot functions, API consumers should understand that some fields are OS-dependent or optional/defaulted.

### Test Signals
No tests in this file; coverage is through submodule tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/sampler/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/sampler/process.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/sampler/process.rs

### Purpose
Samples current-process CPU, memory, uptime, disk I/O, file descriptors, task count, lock counts, and platform-specific process counters.

### Important APIs, Types, And Functions
`ProcessResourceSnapshot` contains CPU percent, memory bytes, and uptime. `ProcessStatusSnapshot` maps selected `sysinfo::ProcessStatus` variants to stable numeric categories. `ProcessSystemSnapshot` contains lock counts, CPU total seconds, task count, disk bytes, platform I/O counters, start/uptime, file descriptor limits/open counts, syscall totals, resident/virtual/peak memory, status, and status value. APIs are `snapshot_process_resource`, `snapshot_process_system`, and `snapshot_process_resource_and_system`.

### Control Flow
A static `OnceLock<Mutex<System>>` caches a sysinfo `System`. Snapshot refreshes the current PID with `ProcessRefreshKind::everything`, obtains platform stats and lock counts, then maps sysinfo process fields plus platform optional values into resource and system snapshots. If the process is missing, default snapshots are returned.

### State And Persistence
The cached `System` object persists for process lifetime and is protected by a mutex that tolerates poison by taking the inner value. Snapshots are immutable value copies.

### Dependencies And Integration Points
Depends on `sysinfo`, `process_lock_metrics`, and sampler system wrapper. Re-exported from sampler/mod and lib.rs. Intended for periodic resource telemetry collection.

### Risks
Sampling uses a global mutex, so high-frequency sampling can contend. Some fields are semantically inherited from Go-style metrics (`go_routine_total`) but actually map to sysinfo tasks, which can confuse dashboard naming. Platform stats default to zero when unavailable, so consumers need to distinguish unavailable from true zero through platform knowledge.

### Test Signals
Tests validate status mapping and that snapshots are collectable for the current process.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/sampler/process.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/sampler/system.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/sampler/system.rs

### Purpose
Thin wrapper exposing platform-specific process counters through the sampler namespace.

### Important APIs, Types, And Functions
`snapshot_process_platform` returns `ProcessPlatformSnapshot` by calling `crate::snapshot_process_platform_stats()`.

### Control Flow
The function is a direct delegation.

### State And Persistence
No state.

### Dependencies And Integration Points
Depends on `ProcessPlatformSnapshot` and the crate-level re-export of process platform stats. Used by sampler re-exports and callers that want only platform-specific counters.

### Risks
All risks are inherited from `process_lock_metrics::snapshot_process_platform_stats`: OS-dependent availability, external command failures on some platforms, and default/optional values.

### Test Signals
No local tests; behavior is covered by process/platform tests elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/sampler/system.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/system_path_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/system_path_metrics.rs

### Purpose
Records failures involving system paths, categorized by path kind, operation, and reason.

### Important APIs, Types, And Functions
Exports `record_system_path_failure(path_kind, operation, reason)`.

### Control Flow
The function increments `rustfs_system_path_failures_total` with the three static labels.

### State And Persistence
No local state; aggregation is external via the metrics recorder.

### Dependencies And Integration Points
Re-exported from `lib.rs` and intended for code that interacts with OS paths, directories, or files where failures should be visible in system metrics.

### Risks
The labels are `&'static str`, which encourages low cardinality. Callers must still define a stable vocabulary. There are no tests in this file.

### Test Signals
No local unit tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/system_path_metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/timeout_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/timeout_metrics.rs

### Purpose
Emits timeout and progress metrics and defines a summary struct for operation timeout/stall/success/failure rates.

### Important APIs, Types, And Functions
Exports `record_timeout_event`, `record_operation_duration`, `record_dynamic_timeout`, `record_operation_progress`, `record_stalled_operation`, `record_operation_completion`, and `TimeoutMetricsSummary`. The summary stores total operations, timed out, stalled, successful, and failed counts with timeout/stall/success rate helpers.

### Control Flow
Recorders emit counters, gauges, and histograms. Dynamic timeout records size and timeout gauges plus a size histogram. Completion records success/failure through a status label. Summary rate methods return zero when total operations is zero.

### State And Persistence
No recorder state. Summary is plain caller-owned memory.

### Dependencies And Integration Points
Pairs with `io-core/src/timeout_wrapper.rs` but does not depend on it directly. Re-exported from `lib.rs`.

### Risks
Operation labels are dynamic strings and can be high cardinality if callers include IDs or paths. `record_dynamic_timeout` records a size histogram but not a timeout histogram, only a timeout gauge, so historical timeout distribution may be incomplete depending on backend behavior.

### Test Signals
Tests execute all recorders and validate summary rate calculations.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/timeout_metrics.rs -->
