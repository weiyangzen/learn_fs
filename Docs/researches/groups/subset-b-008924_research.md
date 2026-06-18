# Research Group subset-b-008924

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/cache.rs -->
# sources/storage-engines/tikv/src/coprocessor/cache.rs

Purpose: implements the fast coprocessor-cache hit path. `CachedRequestHandler` is a trivial `RequestHandler` used when the request carries a cache match version equal to the snapshot data version. Instead of building and executing DAG/analyze/checksum logic, it returns a `coprocessor::Response` marked `is_cache_hit`.

Important APIs: `CachedRequestHandler::new` reads `SnapshotExt::get_data_version`; `builder` returns a `RequestHandlerBuilder`; `handle_request` sets `is_cache_hit` and optionally `cache_last_version`. Control flow is intentionally one step: endpoint selects this handler, then the handler returns an empty data response with cache metadata.

State and persistence: the only stored state is optional `data_version`. It is not persisted and is derived from the read snapshot. Dependencies are `tikv_kv::SnapshotExt`, `tikv_alloc::MemoryTraceGuard`, and the coprocessor `RequestHandler` trait.

Integration points: selected by `Endpoint::handle_unary_request_impl` when `ReqContext.cache_match_version` matches `snapshot.ext().get_data_version()`. Risks are mostly semantic: cache-hit responses must preserve version metadata and must not be used for non-matching versions. Test signals are indirect through endpoint cache behavior; this file has no local tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/cache.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/checksum.rs -->
# sources/storage-engines/tikv/src/coprocessor/checksum.rs

Purpose: handles TiDB checksum requests over MVCC snapshots. `ChecksumContext<S>` owns a `ChecksumRequest` and a `RangesScanner<TikvStorage<SnapshotStore<S>>, ApiV1>` that scans key/value rows across requested ranges.

Important APIs: `ChecksumContext::new` builds a `SnapshotStore` with request isolation, fill-cache, bypass-lock, and access-lock settings, then wraps it in `TikvStorage` and `RangesScanner`. `handle_request` currently accepts only `ChecksumAlgorithm::Crc64Xor`, applies optional old/new prefix rewrite rules, scans all rows, verifies scanned keys start with the expected new prefix, computes xor CRC64 values through `checksum_crc64_xor`, and serializes `ChecksumResponse`. `collect_scan_statistics` forwards scanner storage stats.

State and persistence: all state is request-local. It reads from a snapshot but writes no persisted data. Dependencies include protobuf `ChecksumRequest/Response`, `crc64fast`, `tidb_query_common::RangesScanner`, and TiKV storage abstractions.

Integration points: built by `Endpoint::parse_request_and_check_memory_locks_impl` for `REQ_TYPE_CHECKSUM`; checksum requests are allowed during flashback. Risks include prefix-length arithmetic (`old_prefix.len() - new_prefix.len()`), unsupported algorithms, and strict ApiV1 storage format. Test signals are indirect; `checksum_crc64_xor` is exported from `mod.rs`, but this file has no local test module.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/checksum.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/config_manager.rs -->
# sources/storage-engines/tikv/src/coprocessor/config_manager.rs

Purpose: implements online configuration for coprocessor memory quota. `CopConfigManager` holds an `Arc<MemoryQuota>` shared with `Endpoint`.

Important APIs: `CopConfigManager::new` stores the quota handle. The `ConfigManager::dispatch` implementation removes `end_point_memory_quota` from a `ConfigChange`; if the value is not `ConfigValue::None`, it converts it to `ReadableSize` and calls `MemoryQuota::set_capacity`.

Control flow is direct and synchronous. The config subsystem invokes `dispatch`, the manager selectively handles the coprocessor memory quota key, and all other keys are ignored. State is in the shared `MemoryQuota`; no durable persistence is performed here.

Dependencies are `online_config`, `tikv_util::config::ReadableSize`, and `tikv_util::memory::MemoryQuota`. Integration point is `Endpoint::config_manager`, which boxes this manager for server configuration plumbing. Risks: key spelling must match the server config field, conversion assumes the config value carries a size, and reducing capacity can cause subsequent request admission failures. There are no local tests; endpoint memory-quota tests cover the shared quota effect.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/config_manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/dag/mod.rs -->
# sources/storage-engines/tikv/src/coprocessor/dag/mod.rs

Purpose: bridges TiKV coprocessor DAG requests into the TiDB query executor runner. It builds batch DAG handlers, adapts extra-region storage access, and converts query-engine results/errors into coprocessor protobuf responses.

Important APIs/types: `DagHandlerBuilder<R,S,F>` captures request, ranges, store, optional extra-region accessor, deadline, batch limits, paging, max-keys-read, cache flags, and quota limiter. `build` increments the DAG request metric and returns a boxed `BatchDagHandler`. `ExtraTiKVStorageAccessor<R>` wraps a `RegionStorageAccessor` and converts its storage into `TikvStorage`. `BatchDagHandler::new` calls `BatchExecutorsRunner::from_request`; its `RequestHandler` impl delegates unary and streaming execution and exposes scan stats/summary.

Control flow: endpoint parses DAG protobuf, constructs `DagHandlerBuilder`, then the handler runner executes DAG batches. `handle_qe_response` serializes `SelectResponse`, sets returned range and cache metadata, maps storage errors to coprocessor errors, maps deadline to `Error::DeadlineExceeded`, and embeds evaluate errors inside the select response. `handle_qe_stream_response` performs the analogous streaming conversion for `StreamResponse`.

State is request-local except runner-held scan/cache state. Dependencies are `tidb_query_executors`, `tidb_query_common`, API-version key formats, quota limiter, and coprocessor metrics. Risks include error-shape compatibility with TiDB, cacheability correctness across extra-region reads, and the interaction of paging/max-keys limits. Local tests cover response conversion, storage/deadline/evaluate error mapping, and cache metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/dag/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/dag/storage_impl.rs -->
# sources/storage-engines/tikv/src/coprocessor/dag/storage_impl.rs

Purpose: implements `tidb_query_common::storage::Storage` on top of TiKV's `Store` abstraction so query executors can scan MVCC data.

Important APIs/types: `TikvStorage<S>` stores the underlying `Store`, an optional active scanner, accumulated CF statistics, and `NewerTsCheckState` for cacheability. `begin_scan` drains stats from the prior scanner, preserves any newer-ts detection, builds raw-key lower/upper bounds, and creates a new TiKV scanner. `scan_next_entry` returns owned key/value/optional commit-ts entries. `get_entry` performs point gets through `incremental_get_entry`. `met_uncacheable_data` reports whether newer-ts data was observed. `collect_statistics` merges store/scanner stats into the destination and resets the backlog.

State and persistence: no writes are persisted; scanner state, statistics, and cacheability state are request-local. Dependencies include `txn_types::Key`, TiKV `Scanner/Store/Statistics`, and query-engine `OwnedKvPairEntry`.

Integration points: used by DAG, checksum, and analyze scanning paths. Risks include `scan_next_entry` relying on `begin_scan` having been called, correct conversion from raw query ranges to `txn_types::Key`, and accurate newer-ts reporting for coprocessor cache decisions. Tests are indirect through DAG/analyze/checksum endpoint behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/dag/storage_impl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/endpoint.rs -->
# sources/storage-engines/tikv/src/coprocessor/endpoint.rs

Purpose: central coprocessor entry point. `Endpoint<E>` parses protobuf requests, checks locks and deadlines, retrieves snapshots, builds typed request handlers, schedules work on the read pool, enforces memory/concurrency/resource limits, records metrics, and formats responses.

Important APIs/control flow: `new` wires read-pool handle, optional Yatp semaphore, memory quota, concurrency manager, resource tagging/control, timeouts, row limits, and quota limiter. `parse_request_and_check_memory_locks_impl` dispatches by API version and request type: DAG builds `SnapshotStore` plus `DagHandlerBuilder`; analyze builds `AnalyzeContext`; checksum builds `ChecksumContext`. It also applies start-ts fallbacks, request tags, cache-match version, recursion limit, tracker request type, and in-memory lock checks. `get_snapshot_with_timeout` obtains a TLS-engine snapshot bounded by the request deadline.

Unary flow: `parse_and_handle_unary_request` rejects busy read pools early, processes embedded batch tasks, parses the main request, and schedules `handle_unary_request_impl`. The implementation records input bytes, checks schedule/snapshot deadlines, validates bucket versions, optionally swaps in `CachedRequestHandler`, runs the handler through deadline and semaphore interceptors, collects execution/storage stats, adds exec details and bucket version, and converts errors through `make_error_response`. Streaming flow mirrors this but yields multiple responses through an mpsc channel and holds a semaphore permit for the stream.

State/persistence: endpoint owns shared runtime controls but persists no data. Per-request state lives in `ReqContext`, `Tracker`, snapshot stores, and handlers. Dependencies include kvproto/tipb, Yatp read pools, concurrency manager, resource metering/control, quota limiter, `SnapshotExt`, and coprocessor modules. Risks: deadline checks around queued work and snapshot fetch, cache version/bucket version correctness, memory quota accounting, extra-region snapshot safety, lock checking for replica/stale reads, and error mapping compatibility. Tests are broad: invalid request handling, recursion limit, queue saturation, unary/stream errors, response byte accounting, stream termination/backpressure, timing details, deadlines, memory locks, memory quota, snapshot timeout, and extra-region accessor behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/endpoint.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/error.rs -->
# sources/storage-engines/tikv/src/coprocessor/error.rs

Purpose: defines the coprocessor error model and conversions from lower storage/query layers. `Error` distinguishes retryable region errors, lock conflicts, deadline, admission, memory quota, max-ts update, default-CF missing values, and generic other errors.

Important APIs: `Result<T>` aliases `std::result::Result<T, Error>`. `From` implementations convert boxed errors, query `StorageError`/`EvaluateError`, `tidb_query_common::Error`, KV/MVCC/txn errors, deadline errors, datatype/codec errors, and `MemoryQuotaExceeded`. `ErrorCodeExt::error_code` maps variants to TiKV error codes.

Control flow: lower-level errors are collapsed into response-relevant categories. Region and lock errors preserve structured protobuf details; default-not-found is separated for logging/response treatment; unknowns become `Other`. `From<StorageError>` attempts to downcast back to coprocessor `Error`.

State/persistence: none. Dependencies are TiKV storage error types, `kvproto`, `error_code`, `thiserror`, and memory quota. Integration points are endpoint response formatting, DAG storage error conversion, and query engine storage bridges. Risks are lossy conversion into `Other`, downcast failure text hiding original structure, and ensuring newly introduced storage errors receive appropriate structured mappings. No local tests; endpoint tests validate several response conversions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/interceptors/concurrency_limiter.rs -->
# sources/storage-engines/tikv/src/coprocessor/interceptors/concurrency_limiter.rs

Purpose: provides a future wrapper that lets light coprocessor tasks run without taking a semaphore, while forcing heavier tasks to acquire a permit after a configured execution-time threshold.

Important APIs/types: `limit_concurrency(fut, semaphore, time_limit_without_permit)` constructs `ConcurrencyLimiter`. The internal state machine has `NotLimited`, `Acquiring(Instant)`, and `Acquired { _permit }`. Its `Future::poll` tracks elapsed time across pending polls; once elapsed time exceeds the threshold, it polls semaphore acquisition before continuing the wrapped future.

State and metrics: state is per future. Metrics increment unacquired/acquired counters, waiting gauge, and semaphore wait histogram. No persistent state exists. Dependencies are `tokio::sync::Semaphore`, `pin_project`, `futures::FutureExt`, and coprocessor metrics.

Integration points: unary endpoint handling wraps request execution with `limit_concurrency` when a Yatp-backed endpoint has a semaphore. Streaming takes a permit up front instead. Risks include undercounting CPU-heavy futures that do not yield, because elapsed execution is observed only around polls, and fairness depending on semaphore order. Tests verify light tasks complete without permits and heavy tasks serialize behind semaphore acquisition.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/interceptors/concurrency_limiter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/interceptors/deadline.rs -->
# sources/storage-engines/tikv/src/coprocessor/interceptors/deadline.rs

Purpose: wraps a future with deadline checks before every poll. It is a small interceptor used to stop yieldable coprocessor work after its request deadline.

Important APIs/types: `check_deadline(fut, deadline)` returns `DeadlineChecker<F>`, a pinned future whose `poll` calls `deadline.check()?` before polling the inner future and maps a ready inner result into `Ok`.

State and persistence: only the inner future and `Deadline` are stored. There is no persistent state. Dependencies are `tikv_util::deadline::{Deadline, DeadlineError}` and `pin_project`.

Integration points: `Endpoint::handle_unary_request_impl` wraps `handler.handle_request()` before tracking and optional semaphore limiting. Streaming code currently performs explicit deadline checks around scheduling and snapshot, but not this per-poll wrapper around each streaming handler call. Risks: non-yielding blocking work cannot be interrupted until it returns to poll; callers must convert `DeadlineError` into coprocessor `Error::DeadlineExceeded`. The local Tokio test verifies short work succeeds and long yieldable work returns a deadline error.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/interceptors/deadline.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/interceptors/mod.rs -->
# sources/storage-engines/tikv/src/coprocessor/interceptors/mod.rs

Purpose: module facade for coprocessor execution interceptors. It declares `concurrency_limiter` and `deadline`, then re-exports `limit_concurrency` and `check_deadline`.

Important API surface: consumers import from `coprocessor::interceptors::*` instead of depending on submodule paths. There is no runtime control flow, state, persistence, or tests in this file.

Dependencies and integration: used by `endpoint.rs` to apply deadline and concurrency wrappers around handler futures. Risk is limited to public API organization: renaming or changing exports breaks endpoint imports and any future interceptor users.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/interceptors/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/metrics.rs -->
# sources/storage-engines/tikv/src/coprocessor/metrics.rs

Purpose: defines Prometheus metrics, static label enums, TLS-local aggregation, PD read-flow reporting, and memory-quota gauges for coprocessor.

Important APIs/types: label enums include request tags, CFs, scan kinds, wait types, memory-lock check results, analyze metric kinds, and semaphore acquisition types. Registered metrics cover request duration/handle/wait/handler-build, request errors, scan keys/details, DAG count, response bytes, semaphore waits, memory-lock checks, analyze I/O counters/ratio, and memory quota. `CopLocalMetrics` stores TLS scan details and `ReadStats`. `tls_flush` emits Prometheus counters and PD read stats through a `FlowStatsReporter`. `tls_collect_scan_details`, `tls_collect_read_flow`, and `tls_collect_query` aggregate per-thread data. `register_coprocessor_memory_quota_metrics` registers a custom collector exposing capacity and in-use bytes.

State and persistence: all state is in process-local Prometheus registries and thread-local buffers; PD read stats are flushed by read-pool tickers. No durable writes occur. Dependencies include `prometheus`, `prometheus_static_metric`, raftstore read stats, PD bucket metadata, server GC metric enums, and `MemoryQuota`.

Integration points: endpoint/tracker collect stats, readpool tickers call `tls_flush`, analyze code increments analyze metrics, and concurrency/deadline paths update semaphore/deadline-related metrics. Risks include high cardinality if labels expand, TLS metrics not flushing on idle/stopped threads, duplicate memory-quota collector registration warnings, and stale PD flow if tickers fail. Test-only helpers expose and clear local read stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/mod.rs -->
# sources/storage-engines/tikv/src/coprocessor/mod.rs

Purpose: top-level coprocessor module. It documents the subsystem, declares submodules, exports endpoint/error/checksum pieces, defines request type constants, and provides shared request context and handler traits.

Important APIs/types: `RequestHandler` is the async trait implemented by cache, DAG, analyze, checksum, and test fixtures. It supports unary `handle_request`, streaming `handle_streaming_request`, scan statistics/summary collection, and boxing. `RequestHandlerBuilder<Snap>` is a one-shot closure from snapshot and `ReqContext` to boxed handler. `ReqContextInner` stores protobuf context, ranges, deadline, peer, scan direction, start ts, bypass/access lock sets, cache match version, lower/upper bounds, perf level, and flashback allowance. `ReqContext` wraps it in `Arc` and implements heap sizing. `build_task_id` combines task-id low bits with start-ts or random fallback.

State and persistence: context is immutable per request and shared across async tasks; memory trace roots for coprocessor/analyze are global process state. Dependencies include kvproto, `Deadline`, `PerfLevel`, `TsSet`, `MemoryTrace`, and storage `Statistics`.

Integration points: endpoint constructs `ReqContext`; handlers consume it; tracker/metrics use request tags; analyze uses `MEMTRACE_ANALYZE`. Risks include deadline derivation precedence (`max_execution_duration_ms` overrides config), lower/upper bound assumptions on sorted ranges, and panics if unsupported handler methods are called. Tests cover task-id composition, deadline override behavior, and constructor equivalence.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/readpool_impl.rs -->
# sources/storage-engines/tikv/src/coprocessor/readpool_impl.rs

Purpose: builds coprocessor Yatp future pools with proper thread-local engine setup and metric flushing.

Important APIs/types: `FuturePoolTicker<R>` implements `PoolTicker::on_tick` by calling `tls_flush(&reporter)`. `build_read_pool` converts `CoprReadPoolConfig` into three Yatp configs named `cop-low`, `cop-normal`, and `cop-high`; each pool sets TLS engine and foreground read I/O type on worker start, destroys TLS engine on stop, and uses the metric flushing ticker. `build_read_pool_for_test` builds equivalent pools with `DefaultTicker`.

State and persistence: thread-local engine and I/O type are set per worker. Metrics are flushed through the reporter; no durable state is written. Dependencies include file-system I/O type markers, Yatp pool builder, coprocessor metrics, and TiKV engine/TLS helpers.

Integration points: server initialization uses this to create read pools consumed by `Endpoint`; tests use the test builder. Risks include config length assumptions (`assert_eq!(configs.len(), 3)`), holding cloned engines behind `Arc<Mutex<_>>` during setup, and missing TLS engine setup causing unsafe endpoint snapshot calls to fail. Test signal is indirect through many endpoint tests using `build_read_pool_for_test`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/readpool_impl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/statistics/analyze.rs -->
# sources/storage-engines/tikv/src/coprocessor/statistics/analyze.rs

Purpose: implements table-column analyze algorithms: legacy column sampling, full row sampling, FM sketches, optional CM sketches, primary-key/common-handle histograms, column-group stats, quota accounting, and memory tracing.

Important APIs/control flow: `RowSampleBuilder::new` builds a `BatchTableScanExecutor` over `TikvStorage`; `collect_column_stats` loops over `next_batch`, observes CPU and I/O through `QuotaLimiter` samples, collects per-batch storage stats, encodes each row column, handles string collations through sort keys, updates column and column-group FM sketches, samples rows through either reservoir or Bernoulli collectors, consumes quota, and finally copies single-column group stats from matching column stats. `merge_storage_stats_into` exposes accumulated stats to the analyze context.

`RowSampleCollector` abstracts row sampling. `BaseRowSampleCollector` tracks null counts, total row count, FM sketches, total sizes, RNG, memory usage, and memory trace reporting. `BernoulliRowSampleCollector` samples each row with a configured probability. `ReservoirRowSampleCollector` keeps a bounded heap of weighted samples. `SampleBuilder` handles legacy column/mixed analyze: scans table rows, optionally builds PK/common-handle histograms, rewrites INT/UINT/DURATION encodings for CM-sketch compatibility with TiDB, applies collation sort keys, and fills `SampleCollector`s. Result wrappers convert analyze results to tipb responses.

State/persistence: all stats are request-local until serialized; no storage writes occur. Global memory trace `MEMTRACE_ANALYZE` is adjusted as sample buffers grow/shrink. Dependencies include TiDB datatype codecs/collations, `BatchTableScanExecutor`, histogram/cmsketch/fmsketch modules, quota limiter, analyze metrics, and protobuf tipb types. Risks include encoding compatibility with TiDB, memory accounting leaks on early return/drop, quota sampling across async polls, random sampling variance, and `data[0]` assumptions for encoded values. Tests cover sample collector counts, reservoir and Bernoulli sampling distribution, abnormal zero-size sampling, memory trace cleanup, plus benches for column and group collection.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/statistics/analyze.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/statistics/analyze_context.rs -->
# sources/storage-engines/tikv/src/coprocessor/statistics/analyze_context.rs

Purpose: request handler for analyze coprocessor requests. It selects the correct analyze algorithm, constructs scanners/builders, serializes tipb responses, and exposes storage statistics.

Important APIs/types: `AnalyzeVersion` maps protobuf version integers to V1/V2. `AnalyzeContext<S,F>` stores the request, optional `TikvStorage<SnapshotStore<S>>`, key ranges, accumulated storage stats, quota limiter, and auto-analyze flag. `new` constructs a `SnapshotStore` with request isolation/cache/lock settings and wraps it in `TikvStorage`. Helper methods handle column, mixed, full-sampling, and index analyze.

Control flow in `handle_request`: `TypeIndex`/`TypeCommonHandle` validates table ranges, builds a key-only `RangesScanner`, and calls `handle_index`. Index analysis parses record/index key datums, appends histogram values, fills FM and optional CM sketches, and for V2 maintains TopN by grouping repeated sorted values and moving them from CM sketch into TopN. `TypeColumn` and `TypeMixed` use `SampleBuilder`; `TypeFullSampling` uses `RowSampleBuilder` with quota limiter; `TypeSampleIndex` returns not implemented. Successful data is wrapped in `MEMTRACE_ANALYZE`; `Error::Other` is converted to `Response.other_error`.

State/persistence: request-local only; `storage` is an `Option` so it can be taken exactly once. Dependencies include analyze builders, sketches, histogram, table codecs, `RangesScanner`, and quota limiter. Integration point is endpoint's analyze request builder. Risks include `AnalyzeVersion::from` panic on unknown versions, strict key format validation, TopN heap correctness, and response error-shape differences between `Other` and structured errors. No local tests in this file; analyze algorithm tests live in `analyze.rs` and sketch modules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/statistics/analyze_context.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/statistics/cmsketch.rs -->
# sources/storage-engines/tikv/src/coprocessor/statistics/cmsketch.rs

Purpose: implements Count-Min Sketch for approximate point-query frequency estimates, plus TopN extraction support for analyze V2.

Important APIs/types: `CmSketch::new(depth, width)` returns `None` if either dimension is zero. `insert` hashes bytes with Murmur3 x64 128-bit and increments one counter per row using double hashing. `sub` removes counts from the sketch with saturating row subtraction and decrements total count. `push_to_top_n` records exact heavy-hitter entries. `From<CmSketch> for tipb::CmSketch` serializes rows and TopN entries.

State and persistence: the sketch holds in-memory counter rows, total count, and TopN data; it is serialized into analyze responses but not persisted directly by TiKV. Dependencies are `mur3`, `tipb`, and test-only datatype/zipf helpers.

Integration points: `SampleCollector` and index analyze paths insert encoded column/index values; analyze V2 subtracts TopN values from the CM sketch and stores them separately. Risks include `sub` using `self.count -= cnt` without saturating the total, parameter zero disabling the sketch, and estimator compatibility with TiDB's expected encoding. Tests verify deterministic Murmur hashes and average error on Zipf-distributed encoded values.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/statistics/cmsketch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/statistics/fmsketch.rs -->
# sources/storage-engines/tikv/src/coprocessor/statistics/fmsketch.rs

Purpose: implements TiDB-compatible Flajolet-Martin sketch for approximate NDV estimation during analyze.

Important APIs/types: `FmSketch::new(max_size)` creates a sketch with mask level zero and a hash set sized to `max_size + 1`. `insert` hashes input bytes with Murmur3 and delegates to `insert_hash_value`. `insert_hash_value` skips hashes filtered by the current mask, inserts retained hashes, and when the set exceeds `max_size`, advances the mask and prunes hashes not matching the new trailing-zero level. `From<FmSketch> for tipb::FmSketch` serializes the mask and hash set.

State and persistence: in-memory mask and hash set are request-local, then serialized in analyze responses. Dependencies are `collections::HashSet`, `mur3`, and `tipb`.

Integration points: column, row sampling, column-group, index, and common-handle analyze paths use FM sketches to estimate distinct values. Risks include poor behavior with extremely small `max_size`, sensitivity to hash compatibility with TiDB, and memory usage proportional to the configured sketch size. Tests port TiDB expectations for NDV estimates over generated data and verify pruning when `max_size` is two.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/coprocessor/statistics/fmsketch.rs -->
