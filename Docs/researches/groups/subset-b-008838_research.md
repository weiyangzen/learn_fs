# subset-b-008838 Research

Grouped research report for the requested TiKV PD client, profiler, raft-log-engine, and raftstore-v2 source files. Each section is source-tree aligned and wrapped for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/src/meta_storage.rs -->
# sources/storage-engines/tikv/components/pd_client/src/meta_storage.rs

Purpose: Defines the PD meta-storage client abstraction, a trimmed etcd-like key/value API used by TiKV callers that need generic metadata storage through PD. It wraps protobuf requests from `kvproto::meta_storagepb` and exposes a typed trait so callers can compose decorators such as source tagging and response checking.

Important APIs/types/functions: `Get`, `Put`, `Watch`, and `Delete` are builder-style request wrappers. `Get::of`, `prefixed`, `range_to`, `rev`, and `limit` control exact, prefix, range, revision, and limit scans. `Put::fetch_prev_kv` requests prior data. `Watch::from_rev` and `with_prev_kv` configure streaming watches. `Source` names known callers (`LogBackup`, `ResourceControl`, `RegionLabel`). `Sourced<S>` injects the caller string into every request header. `Checked<S>` and `CheckedStream<S>` convert response-header errors into `crate::Error`. `MetaStorageClient` is the core async trait with `get`, `put`, `delete`, and streaming `watch`; an `Arc<S>` forwarding impl makes shared clients usable directly.

Control flow: Request builders mutate protobuf inner messages. `Sourced` wraps each trait call, mutates the request header, then forwards to the inner client. `Checked` maps each future or stream event through `check_resp_header`, returning `DataCompacted` distinctly from unknown metadata errors.

State and persistence behavior: This file itself stores no local state beyond wrapper fields. Persistence is remote, in PD meta storage. The `INF = [0]` sentinel and `codec::next_prefix_of` encode etcd-compatible infinity ranges for full-prefix requests.

Dependencies and integration points: It depends on `futures::Stream`, `kvproto::meta_storagepb`, `tikv_util::codec`, and crate-level `PdFuture`, `Result`, and `Error`. It is constructed from the PD client channel in `pd_client::util::Client` and is consumed by higher-level TiKV services that need PD-backed metadata.

Risks: Prefix range handling relies on `[0]` matching etcd's infinity convention; misuse could create too-wide or too-narrow watches. `CheckedStream` uses an unsafe pin projection, although the projection is trivial. `Source` is a closed enum, so new metadata callers must add a variant or lose source attribution. `GlobalConfigNotFound`-style PD errors are not represented here, only meta-storage error kinds.

Test signals: No tests are local to this file. Coverage is expected through PD client integration tests and consumers that exercise meta-storage `get/put/delete/watch`, especially `DataCompacted` watch behavior and prefixed range requests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/src/meta_storage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/src/metrics.rs -->
# sources/storage-engines/tikv/components/pd_client/src/metrics.rs

Purpose: Registers all Prometheus metrics used by the PD client crate. The file centralizes request latency, reconnect status, heartbeat/bucket reporting, store size, region traffic histograms, request forwarding, and pending TSO counters.

Important APIs/types/functions: `make_static_metric!` creates label enums `PDRequestEventType`, `PDReconnectEventKind`, and `StoreSizeEventType`, plus statically typed metric vectors `StoreSizeEventIntrVec`, `PDRequestEventHistogramVec`, and `PDReconnectEventCounterVec`. `lazy_static!` exports `PD_REQUEST_HISTOGRAM_VEC`, `PD_HEARTBEAT_COUNTER_VEC`, `PD_BUCKETS_COUNTER_VEC`, `PD_RECONNECT_COUNTER_VEC`, `PD_PENDING_HEARTBEAT_GAUGE`, `PD_PENDING_BUCKETS_GAUGE`, `PD_VALIDATE_PEER_COUNTER_VEC`, `STORE_SIZE_EVENT_INT_VEC`, region read/write histograms, `REQUEST_FORWARDED_GAUGE_VEC`, and `PD_PENDING_TSO_REQUEST_GAUGE`.

Control flow: There is no runtime control flow beyond lazy initialization. Metrics register on first access and unwrap registration failures, matching TiKV's expectation that metric names are unique process-wide.

State and persistence behavior: The only state is in Prometheus collectors held in global statics. Nothing is persisted. Counters and gauges are process-lifetime observability state, reset on restart.

Dependencies and integration points: The file uses `prometheus`, `prometheus_static_metric`, and `lazy_static`. It is integrated by `pd_client::util` for request durations, reconnect outcomes, forwarded-host gauges, heartbeat/bucket pending gauges, and by `pd_client::tso` for pending timestamp request counts.

Risks: Metric name or label changes affect dashboards and alerting. `unwrap()` on registration can panic if another crate registers the same metric name. Some histogram descriptions appear copy-pasted, for example read histograms say "written" in help text; this is low functional risk but can confuse operators.

Test signals: No local unit tests. Validation normally comes from compile-time label generation and runtime metric registration during PD client tests or full TiKV startup.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/src/tso.rs -->
# sources/storage-engines/tikv/components/pd_client/src/tso.rs

Purpose: Implements the low-level Timestamp Oracle worker used by `PdClient::get_tso`. It batches many caller timestamp requests into streaming PD `TsoRequest`s and distributes returned physical/logical timestamps back to individual oneshot callers.

Important APIs/types/functions: `TimestampOracle` owns a bounded `mpsc::Sender<TimestampRequest>` plus a close watch receiver. `TimestampOracle::new` opens the PD bidirectional TSO stream and spawns the `TSO_WORKER_THREAD`. `get_timestamp(count)` returns a future resolving to a composed `txn_types::TimeStamp`. `closed()` lets callers observe worker termination. `run_tso` drives sending and receiving futures concurrently. `TsoRequestStream` implements `Stream<Item=(TsoRequest, WriteFlags)>` and batches up to `MAX_BATCH_SIZE`. `allocate_timestamps` maps one PD tail timestamp and response count back to queued requests.

Control flow: Callers send a `TimestampRequest` containing a oneshot sender and requested count. The worker drains the bounded channel into a request group, sends one `TsoRequest` with the summed count, tracks the group in a FIFO pending queue, and waits for matching PD responses. The response handler pops the oldest group and calculates each caller's logical timestamp by subtracting offsets from PD's tail logical value.

State and persistence behavior: State is in-memory: bounded request channel, pending request queue, and close notification. It persists nothing locally. `MAX_PENDING_COUNT` and the `AtomicWaker` prevent unbounded pending growth by pausing request-stream polling until responses drain.

Dependencies and integration points: It uses `grpcio`, `kvproto::pdpb::PdClient`, `futures`, `tokio` channels, TiKV thread naming utilities, and `PD_PENDING_TSO_REQUEST_GAUGE`. It is created by `pd_client::util::PdConnector`/`Client` when a PD connection is established or reconnected.

Risks: The worker assumes PD responses arrive in request order and with exactly matching `count`; mismatch errors terminate the worker. Logical subtraction assumes PD returned a sufficient tail logical value. `request_tx` is bounded to `MAX_BATCH_SIZE`, so overloaded callers apply backpressure. The spawned thread uses `expect`, so thread creation failure panics.

Test signals: No local tests. Important integration signals are TSO monotonicity, count batching, worker shutdown after stream error, pending gauge accuracy, and reconnection replacing the oracle.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/src/tso.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/src/util.rs -->
# sources/storage-engines/tikv/components/pd_client/src/util.rs

Purpose: Provides the PD client connection machinery: endpoint validation, leader/follower forwarding, reconnect/backoff, synchronous and asynchronous request retry wrappers, heartbeat/resource stream refresh, response-header conversion, and bucket-stat helper functions.

Important APIs/types/functions: `TargetInfo` records the target PD URL and optional forwarding hop; `call_option` injects `pd-forwarded-host` metadata. `Inner` holds the active grpc environment, stubs, stream senders/receivers, PD members, TSO oracle, meta-storage stub, resource manager stream, pending counters, reconnect callback, and backoff state. `Client::new`, `update_client`, `request`, `reconnect`, `handle_region_heartbeat_response`, and `on_reconnect` are the core client lifecycle APIs. `Request<Req,F>::execute` implements async retry and reconnect. `sync_request` provides blocking retry behavior. `PdConnector` implements `validate_endpoints`, `connect`, `load_members`, `reconnect_pd`, `connect_member`, `reconnect_leader`, and `try_forward`. Utility helpers include `trim_http_prefix`, `check_resp_header`, `new_bucket_stats`, `find_bucket_index`, and `merge_bucket_stats`.

Control flow: Startup validates configured endpoints, checks duplicate endpoints and cluster-id consistency, loads members, connects to the leader, and optionally builds a `TimestampOracle`. Request execution sends against the current stub, retries retryable errors, and forces reconnect after enough attempts. Reconnect reloads members, uses exponential backoff to suppress storms, tries direct leader connection first, and falls back to follower forwarding when enabled and leader networking is unavailable. `update_client` refreshes heartbeat, bucket, resource manager, TSO, meta-storage, and metrics under a write lock.

State and persistence behavior: This file has no disk persistence. Runtime state is held behind `RwLock<Inner>`, `AtomicU64` pending counters, stream endpoints, cached member metadata, and forwarding gauges. Bucket helpers operate on protobuf stats in memory and merge per-bucket deltas across overlapping bucket key ranges.

Dependencies and integration points: It depends on grpcio, PD/resource/meta-storage protobuf stubs, `SecurityManager`, TiKV timers, failpoints, metrics, `TimestampOracle`, and bucket metadata types. It is the backbone used by the higher-level PD client implementation and by raftstore PD reporting streams.

Risks: Lock ordering is delicate; `sync_request` explicitly drops the read lock before waiting to avoid deadlock with reconnect. Many stream creation failures panic via `unwrap_or_else`, making PD stream setup fatal. Forwarding relies on metadata understood by PD. `load_members` panics if an endpoint belongs to a different nonzero cluster. Bucket range helpers assume valid bucket key lists with at least two boundaries.

Test signals: Local tests cover `merge_bucket_stats`, `find_bucket_index`, and `ExponentialBackoff`. Failpoints cover cluster-id readiness and leader connection/reconnect paths. Broader integration tests should validate endpoint mismatch, forwarding, reconnect callbacks, and stream refresh.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/pd_client/src/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/profiler/Cargo.toml -->
# sources/storage-engines/tikv/components/profiler/Cargo.toml

Purpose: Defines the `profiler` crate, a small optional profiling helper for TiKV developers. It is not published and exists to expose zero-cost no-op functions by default and gperftools/Callgrind support when the `profiling` feature is enabled on Unix.

Important APIs/types/functions: The `profiling` feature enables optional dependencies `lazy_static`, `gperftools`, `callgrind`, and `valgrind_request`. The base dependency is `tikv_alloc`, ensuring the crate links TiKV allocation behavior. The `prime` example is declared with `required-features = ["profiling"]`.

Control flow: Cargo feature resolution selects whether `src/lib.rs` compiles `profiler_unix` or `profiler_dummy`. On non-Unix or without `profiling`, consumers still compile against the same public `start`/`stop` API but receive no-op behavior.

State and persistence behavior: No crate-level persistence is configured. When profiling is enabled, runtime output may be produced by gperftools into a profile file chosen by callers; that behavior is in `profiler_unix.rs`, not the manifest.

Dependencies and integration points: The manifest integrates external native/profiling crates only under Unix cfg and optional feature gates. This reduces normal build footprint and avoids requiring gperftools or valgrind-related dependencies for production builds.

Risks: Enabling `profiling` can introduce native dependency and platform availability issues. The example cannot be built unless all optional profiling dependencies resolve. Feature names are part of developer workflows, so changes must coordinate with documentation and scripts.

Test signals: Cargo validates the example under `profiling`. No tests are declared here; build matrix coverage should include default and `--features profiling` on Unix.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/profiler/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/profiler/examples/prime.rs -->
# sources/storage-engines/tikv/components/profiler/examples/prime.rs

Purpose: Provides a concrete profiling example that computes prime numbers while surrounding the hot loop with `profiler::start` and `profiler::stop`. It demonstrates both gperftools CPU profiling and Callgrind instrumentation workflows.

Important APIs/types/functions: `is_prime_number` checks primality using the prepared small-prime list and is marked `#[inline(never)]` to make profiles easier to inspect. `prepare_prime_numbers` builds a table of primes below 10,000 via a sieve. `main` builds the prime table, starts profiling to `./prime.profile`, counts primes from 2 to 49,999, stops profiling, and prints the count.

Control flow: The example first precomputes primes outside the profiled region. The profiled region is only the loop that calls `is_prime_number` for each candidate. This creates a stable, CPU-heavy workload suitable for validating profiler capture.

State and persistence behavior: State is local vectors and counters. gperftools mode writes `prime.profile`; Callgrind mode dumps through Valgrind's normal output mechanisms. There is no application persistence.

Dependencies and integration points: It depends only on the public `profiler` crate API. Cargo requires the `profiling` feature for this example, which ensures `profiler::start` and `stop` are real backend calls on Unix.

Risks: The primality check for values above 10,000 only tests divisibility by primes below 10,000; this is sufficient for the current range but not a general-purpose primality implementation for arbitrarily large values. Running under `valgrind cargo run` is explicitly unsupported because Callgrind detection targets the final example process.

Test signals: No assertions are present; build and manual execution are the validation signals. The printed prime count and generated profile/callgrind output indicate success.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/profiler/examples/prime.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/profiler/src/lib.rs -->
# sources/storage-engines/tikv/components/profiler/src/lib.rs

Purpose: Exposes the public profiling API and selects the backend implementation by platform and feature flag. The public surface is intentionally tiny: callers use `profiler::start(path)` and `profiler::stop()`.

Important APIs/types/functions: The file imports `tikv_alloc`, documents gperftools and Callgrind requirements, and conditionally compiles `profiler_unix` for `all(unix, feature = "profiling")`; otherwise it compiles `profiler_dummy`. It re-exports the selected module's functions so downstream code does not need cfg gates.

Control flow: There is no runtime control flow in this file. Compile-time cfg chooses one of two modules. Documentation explains that Callgrind requires `--instr-atstart=no`, while gperftools writes a profile file named by `start`.

State and persistence behavior: State is delegated to the selected backend. The dummy backend has no state; the Unix backend stores active profiler state in a mutex and may write profile artifacts.

Dependencies and integration points: `tikv_alloc` is externally referenced to keep allocator linkage. The crate is a developer tool used by examples or ad hoc profiling instrumentation without requiring production code to depend on backend details.

Risks: Because both backends export the same names, behavioral differences are feature-dependent: without profiling, `start` returns false and no profiling occurs. Callers that treat `false` as fatal need to account for default builds. Documentation drift from backend behavior would confuse profiling workflows.

Test signals: Compile-time cfg coverage is the main signal. The `prime` example exercises the public API with real profiling enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/profiler/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/profiler/src/profiler_dummy.rs -->
# sources/storage-engines/tikv/components/profiler/src/profiler_dummy.rs

Purpose: Provides the zero-cost fallback profiling API for builds where `profiling` is not enabled or the target is not Unix. It preserves API compatibility without bringing in profiling dependencies.

Important APIs/types/functions: `start(_name)` and `stop()` are both `#[inline]` public functions. `start` accepts any `AsRef<str>` to match the real backend signature and always returns `false`; `stop` also always returns `false`.

Control flow: Both functions return immediately. There is no backend detection, no locking, and no side effect.

State and persistence behavior: No state is stored and no profile output is produced.

Dependencies and integration points: It has no external dependencies. `src/lib.rs` re-exports this module when `not(all(unix, feature = "profiling"))`, allowing all callers to compile against profiler calls even in production-like builds.

Risks: Silent no-op behavior is deliberate but can surprise developers who forget to enable `--features profiling`. The return value is the only programmatic signal that profiling did not start or stop.

Test signals: Build coverage under default features confirms the dummy backend compiles. Behavior is simple enough that dedicated unit tests are not present.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/profiler/src/profiler_dummy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/profiler/src/profiler_unix.rs -->
# sources/storage-engines/tikv/components/profiler/src/profiler_unix.rs

Purpose: Implements real profiling for Unix builds with the `profiling` feature, selecting Callgrind when running under Valgrind and gperftools otherwise.

Important APIs/types/functions: `Profiler` tracks `None`, `GPerfTools`, or `CallGrind`. `ACTIVE_PROFILER: Mutex<Profiler>` serializes profiling sessions. `start(name)` checks for an active session, detects Valgrind with `valgrind_request::running_on_valgrind`, starts Callgrind instrumentation or `gperftools::PROFILER`, records the active backend, and returns true. `stop()` stops the recorded backend and resets the state, or returns false if nothing is active.

Control flow: `start` locks global state and rejects nested profiling. Backend choice is runtime based. `stop` matches the stored backend so it calls the correct stop API; this avoids stopping gperftools after a Callgrind start or vice versa.

State and persistence behavior: Active state is process-global under a mutex. gperftools writes a profile file named by the caller. Callgrind emits through Valgrind. No TiKV engine state is affected.

Dependencies and integration points: It uses `lazy_static`, `gperftools`, `callgrind`, and `valgrind_request`, all enabled by the manifest feature. It is re-exported as the crate public API from `lib.rs`.

Risks: Backend start/stop calls use `unwrap()`, so native backend errors panic. The TODO notes weak multi-thread support; a single global session prevents overlap and may not isolate thread-specific work. Holding the mutex while starting/stopping backend calls could block other callers briefly.

Test signals: No unit tests. The `prime` example under normal execution and Callgrind execution is the intended validation path.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/profiler/src/profiler_unix.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raft_log_engine/Cargo.toml -->
# sources/storage-engines/tikv/components/raft_log_engine/Cargo.toml

Purpose: Defines the `raft_log_engine` crate, TiKV's adapter from the external `raft-engine` crate to TiKV's `engine_traits::RaftEngine` interfaces.

Important APIs/types/functions: The manifest declares a single feature, `failpoints`, forwarding to `raft-engine/failpoints`. Dependencies include `codec`, `encryption`, `engine_traits`, `file_system`, `kvproto`, `raft`, `raft-engine`, logging utilities, `tikv_util`, and `tracker`. `tempfile` is used for tests.

Control flow: Cargo feature selection can enable raft-engine failpoints for testing. The library exports are configured in `src/lib.rs` and implemented primarily in `src/engine.rs`.

State and persistence behavior: The crate's runtime persistence is raft log/state data in raft-engine files. The manifest itself does not configure persistence paths; callers pass `RaftEngineConfig` at runtime.

Dependencies and integration points: It is the bridge between TiKV raftstore code and `raft-engine`, with encryption and I/O rate limiting support. `engine_traits` makes it interchangeable with other raft engine implementations in generic raftstore code.

Risks: Dependency versions and trait contracts are central; mismatches between `raft-engine` and TiKV `engine_traits` can break raft persistence semantics. Failpoint feature exposure should remain test-only.

Test signals: `tempfile` supports local engine tests in `engine.rs`; feature testing should include failpoints where raft-engine failpoint behavior is expected.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raft_log_engine/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raft_log_engine/src/engine.rs -->
# sources/storage-engines/tikv/components/raft_log_engine/src/engine.rs

Purpose: Implements TiKV's `engine_traits` raft engine traits on top of `raft_engine::Engine`, including encrypted/rate-limited filesystem wrappers, raft log batches, raft state metadata, apply/region/flush state storage, compaction, manual purge, and debug scanning.

Important APIs/types/functions: `MessageExtTyped` tells raft-engine how to read `raft::eraftpb::Entry` indexes. `ManagedReader`, `ManagedWriter`, `ManagedFileSystem`, and `ManagedHandle` wrap `DefaultFileSystem` with optional `DataKeyManager` encryption metadata and `IoRateLimiter` throttling. `RaftLogEngine::new`, `exists`, `raft_groups`, `first_index`, and `last_index` wrap the raw engine. `RaftLogBatch` implements `RaftLogBatchTrait` with `append`, state puts, flushed-index records, dirty marks, and recover-state writes. `RaftEngineReadOnly`, `RaftEngineDebug`, and `RaftEngine` impls expose reads, scans, writes, clean/gc, state cleanup, purge, size, and group iteration. `transfer_error` maps raft-engine errors to TiKV engine errors.

Control flow: Writes are staged in `LogBatch` commands and committed through `consume`/`consume_and_shrink` with foreground-write I/O type. State keys are encoded with one-byte prefixes plus big-endian numeric suffixes. Reads for region/apply state scan backwards from a prefix range to find the newest state at or before an apply index. `delete_all_but_one_states_before` scans state records and deletes older duplicates while preserving one record per state kind/CF.

State and persistence behavior: Raft logs and TiKV raftstore metadata are persisted in raft-engine namespaces keyed by raft group id. Store-wide metadata uses raft group id `0`. Encryption metadata is created, linked, rotated, or deleted alongside file create/rename/reuse/delete operations. Manual purge is required and delegates to raft-engine expired-file purge.

Dependencies and integration points: It depends on `engine_traits`, `raft_engine`, `kvproto` raft server protos, encryption, file-system rate limiting, and TiKV logging. Raftstore-v2 uses this engine through generic `RaftEngine` bounds for append, apply-state persistence, compact-log GC, and bootstrap store identity.

Risks: Key-prefix ordering is critical for scans and cleanup; debug assertions guard some assumptions. Path conversion uses `to_str().unwrap()`, so non-UTF8 paths would panic. `cf_to_id` panics for unknown column families. Encryption rename/reuse metadata rollback paths log failures but must remain consistent to prevent unreadable files. `exists` unwraps `read_dir`.

Test signals: Local `test_apply_related_states` verifies initial absence, state/flushed-index writes, reverse lookup by apply index, and latest flushed-index behavior. Additional integration should cover encryption metadata, GC, manual purge, entry fetch, dirty marks, and recovery state.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raft_log_engine/src/engine.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raft_log_engine/src/lib.rs -->
# sources/storage-engines/tikv/components/raft_log_engine/src/lib.rs

Purpose: Defines the public crate boundary for the raft-log-engine adapter. It explains that the crate implements `engine_traits` for `raft_engine` and re-exports the main adapter types.

Important APIs/types/functions: The file enables `feature(test)` under tests, imports TiKV utility macros, declares `mod engine` and `mod perf_context`, and publicly re-exports `ManagedFileSystem`, `RaftEngineConfig`, `RaftLogBatch`, `RaftLogEngine`, `ReadableSize`, and `RecoveryMode`.

Control flow: There is no runtime control flow. Module declarations compile implementation files, and re-exports define what downstream crates can name directly.

State and persistence behavior: State behavior is delegated to `engine.rs`; this file only shapes the public API.

Dependencies and integration points: Downstream raftstore code imports `RaftLogEngine` and config types from this crate rather than from `raft_engine` directly. The documentation also sets a naming convention, though the current exported type is `RaftLogEngine`, not a Rocks-style name.

Risks: Public re-export changes would ripple through TiKV storage code. The crate-level documentation notes work-in-progress abstraction, so trait/API churn should be expected carefully.

Test signals: Compile tests validate exports. Functional tests live in `engine.rs` and higher-level raftstore integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raft_log_engine/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raft_log_engine/src/perf_context.rs -->
# sources/storage-engines/tikv/components/raft_log_engine/src/perf_context.rs

Purpose: Bridges raft-engine performance context counters into TiKV's `engine_traits::PerfContext` and `tracker` metrics.

Important APIs/types/functions: `RaftEnginePerfContext` implements `engine_traits::PerfContext`. `start_observe` resets raft-engine's current perf context with `raft_engine::set_perf_context(Default::default())`. `report_metrics(trackers)` reads `raft_engine::get_perf_context()` and writes derived nanosecond metrics into each `TrackerToken`.

Control flow: A caller starts observation, does raft-engine work, then reports metrics. For each tracker token, `GLOBAL_TRACKERS.with_tracker` updates `store_thread_wait_nanos`, `store_write_wal_nanos`, and `store_write_memtable_nanos`. WAL time sums log write, sync, and rotate durations; memtable time maps to raft-engine apply duration.

State and persistence behavior: This file only observes thread-local or process-local performance counters and writes in-memory tracker metrics. It persists nothing.

Dependencies and integration points: It depends on `raft_engine` perf context APIs, `engine_traits::PerfContext`, and TiKV `tracker`. `RaftLogEngine` returns this type from `PerfContextExt::get_perf_context`.

Risks: Metric field mapping is interpretive; if raft-engine perf context semantics change, tracker metrics could become misleading. Durations are cast from `u128` nanoseconds to `u64`, which is practically safe for normal intervals but technically lossy on extreme values.

Test signals: No local tests. Runtime observability and tracker-based tests are the likely validation path.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raft_log_engine/src/perf_context.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/Cargo.toml -->
# sources/storage-engines/tikv/components/raftstore-v2/Cargo.toml

Purpose: Defines the experimental/next-generation `raftstore-v2` crate, including default test-oriented features and the broad dependency set needed for multi-raft FSMs, tablets, workers, PD interaction, storage engines, and recovery.

Important APIs/types/functions: Default features enable `testexport`, RocksDB KV test engine support, and raft-engine raft test support. Additional feature groups cover failpoints, Rocks engine combinations, and panic test engines. Dependencies include `batch-system`, `engine_traits`, `pd_client`, `raftstore`, `raft`, `kvproto`, `sst_importer`, `resource_control`, `service`, `yatp`, and many TiKV support crates. Two integration test targets are declared: `raftstore-v2-failpoints` and `raftstore-v2-integrations`.

Control flow: Feature resolution determines test exports, failpoints, and engine backends. The crate code itself is organized in `lib.rs` into batch, bootstrap, FSM, operation, raft, router, and worker modules.

State and persistence behavior: Runtime state includes raft logs, region states, tablets, snapshots, and PD-reported metadata. Persistence is through engine trait implementations selected by tests or production integration, not by the manifest.

Dependencies and integration points: The manifest positions raftstore-v2 as a central integration crate spanning PD, storage engines, resource metering/control, gRPC service management, import SST, and asynchronous worker pools.

Risks: The default feature set is test-heavy; production consumers must be deliberate about feature selection. The git dependency on `yatp` master can create reproducibility risk if not locked. Large dependency surface increases compile and behavioral coupling.

Test signals: Declared failpoint and integration tests are the primary crate-level validation targets, requiring matching feature sets.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/batch/mod.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/batch/mod.rs

Purpose: Defines the raftstore-v2 batch-system module boundary. It states that store polling and apply execution use specialized batch systems.

Important APIs/types/functions: The file declares `mod store` and re-exports `StoreContext`, `StoreRouter`, `StoreSystem`, and `create_store_batch_system` from `store.rs`.

Control flow: There is no runtime control flow here. It is a module facade that keeps external users from depending on private batch implementation details while still exposing the core construction and routing types.

State and persistence behavior: State is implemented in `store.rs`; this file has no state.

Dependencies and integration points: It connects `lib.rs` public exports to the concrete store batch system. Other raftstore-v2 modules reference `crate::batch::StoreContext` for per-thread context shared across store and peer FSM delegates.

Risks: Re-export changes affect crate public API and internal imports. The module documentation distinguishes store and apply systems, but only store is declared here; apply FSM scheduling is built through `StorePollerBuilder` and `ApplyFsm`.

Test signals: Compile coverage validates exports. Behavioral tests target `store.rs` and higher-level raftstore-v2 integration suites.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/batch/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/batch/store.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/batch/store.rs

Purpose: Implements the raftstore-v2 store batch system: per-thread `StoreContext`, poll handlers for store and peer FSMs, startup recovery, tablet cleanup, worker/scheduler wiring, router behavior, purge/flush background work, and shutdown.

Important APIs/types/functions: `StoreContext` carries config, transport, metrics, router, tick batches, schedulers, store metadata, raft engine, tablet registry, pools, disk status, snapshot manager, importer, key manager, and latency inspectors. `StorePoller` implements `PollHandler` for `PeerFsm` and `StoreFsm`; `begin`, `handle_control`, `handle_normal`, `light_end`, `end`, and `pause` drive message batches and flush events. `StorePollerBuilder::init` reconstructs peer FSMs from raft groups and cleans stale tablets. `Schedulers` and `Workers` own background channels and threads. `StoreSystem::start`, `shutdown`, `pd_scheduler`, and `refresh_config_scheduler` manage lifecycle. `StoreRouter::send_raft_message` routes known-region raft messages to peer mailboxes and unknown-region messages to the store FSM. `create_store_batch_system` constructs the router/system pair.

Control flow: Startup registers PD reconnect heartbeat callbacks, optionally spawns raft-engine purge tasks, starts write/read/PD/tablet/split-check/refresh-config workers, builds a poller, recovers peers, registers mailboxes, sends `PeerMsg::Start` to peers, then sends `StoreMsg::Start`. Polling drains bounded batches from control and peer queues, delegates to store/peer handlers, invokes raft ready handling, periodically flushes transport, ticks, metrics, and store stats, and forwards latency inspectors to write workers.

State and persistence behavior: Runtime state is in `StoreContext`, worker pools, batch-system mailboxes, `StoreMeta`, recovered peer FSMs, and atomic shutdown markers. Persistence is indirect through raft engine writes, write workers, tablet registry operations, and purge-triggered tablet flushes. Stale tablet directories are removed during recovery, with key-manager cleanup when encryption is enabled.

Dependencies and integration points: This file integrates `batch-system`, PD client callbacks, raftstore worker types, `engine_traits`, `TabletRegistry`, coprocessor host, snapshots, resource control, gRPC service manager, YATP pools, and raftstore-v2 FSM/operation/worker modules.

Risks: Startup ordering is critical: peers must receive `Start` before normal messages, and stale tablet cleanup must not delete merge-source/in-progress state. Manual purge rate calculation depends on KV flush counters. Many worker starts use asserts/unwraps, so startup failures can panic. Router fallback must preserve backpressure semantics for full/disconnected peer queues.

Test signals: Local failpoints pause peer message collection. Crate integration tests should cover startup replay, PD reconnect heartbeat broadcast, purge/manual flush, router fallback for unknown regions, tablet cleanup, shutdown ordering, and refresh config behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/batch/store.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/bootstrap.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/bootstrap.rs

Purpose: Implements re-entrant store and first-region bootstrap logic for raftstore-v2. It allocates IDs through PD, writes store identity and initial region state to the raft engine, and coordinates first-region registration with PD.

Important APIs/types/functions: `Bootstrap<'a, ER>` holds a raft engine reference, cluster id, PD client trait object, and logger. `bootstrap_store` validates existing store identity, checks engine emptiness, allocates a store id, writes `StoreIdent`, and syncs the raft log batch. `bootstrap_first_region` resumes any prepared region, checks if PD is already bootstrapped, prepares initial region state, calls `bootstrap_cluster`, and clears preparation markers. Helpers include `check_store_id_in_engine`, `prepare_bootstrap_first_region`, `check_pd_first_region_bootstrapped`, and `clear_prepare_bootstrap`.

Control flow: Store bootstrap is idempotent: if `StoreIdent` exists and cluster id matches, it returns the existing store id. First-region bootstrap writes a prepare marker before contacting PD so failures can resume. If PD reports another first region, the local prepared state is cleaned. If PD reports the same region, this node treats the previous attempt as successful and clears the marker.

State and persistence behavior: Persistent state is written through `RaftLogBatch`: store ident, prepare-bootstrap region marker, initial region state, and raft local/apply state via `write_initial_states`. Cleanup removes the prepare marker and optionally cleans the prepared region's raft state. All bootstrap writes use `sync=true`.

Dependencies and integration points: It uses `engine_traits::RaftEngine`, `pd_client::PdClient`, `raftstore::store::initial_region`, `operation::write_initial_states`, failpoints, and raft server protobufs. It is used before starting the raftstore-v2 batch system.

Risks: Blocking sleeps retry PD checks for up to 60 * 3 seconds. Cluster-id mismatch is fatal to protect against joining a wrong cluster. Failures between local prepare and PD registration rely on correct marker recovery. Concurrent bootstrap is explicitly not thread safe; methods take `&mut self` to discourage it.

Test signals: Failpoints cover after store bootstrap, after prepare bootstrap, and after PD cluster bootstrap. Integration tests should exercise idempotency, competing bootstrap nodes, existing store identity, dirty non-empty engine, and prepare-marker cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/bootstrap.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/fsm/apply.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/fsm/apply.rs

Purpose: Defines the apply FSM wrapper and scheduler that execute committed raft entries and apply-side tasks for one peer on an async future pool.

Important APIs/types/functions: `ApplyResReporter` abstracts reporting apply results and catch-up log redirects back to a peer mailbox. `ApplyScheduler` wraps a future MPSC sender and exposes `send`. `ApplyFsm<EK,R>` owns a `raft::Apply<EK,R>` and an `ApplyTask` receiver. `ApplyFsm::new` builds the underlying `Apply` with config, peer/region state, tablet registry, read/tablet schedulers, high-priority pool, flush/SST state, optional log recovery, buckets, importer, coprocessor host, and logger. `handle_all_tasks` is the async task loop.

Control flow: The loop waits for either an apply task or a 10-second idle timeout. On idle it releases apply memory, then waits for the next task. For each task it calls `on_start_apply`, handles committed entries, snapshots, unsafe writes, manual flush, bucket refresh, or capture-apply tasks, then `maybe_flush`. It drains immediately available tasks with `try_recv` before doing a final `flush` and `maybe_reschedule`.

State and persistence behavior: Persistence is delegated to `Apply`: applying entries writes to tablets/raft state through engine abstractions, flush state, SST apply state, and result reporting. This wrapper owns the task channel and controls batching/flush cadence, but not the persistent data structures directly.

Dependencies and integration points: It connects `batch_system` mailboxes, `tikv_util::mpsc::future`, raftstore read tasks, tablet workers, SST importer, PD bucket stats, and raftstore-v2 router `ApplyTask`/`ApplyRes`. Peer FSMs create and schedule apply FSMs during startup and raft ready handling.

Risks: `ApplyScheduler::send` unwraps, so sending after receiver shutdown panics. Idle memory release depends on timeout behavior. Long task bursts can defer final flush until the local queue drains. Correctness depends on `Apply::maybe_flush` and `flush` preserving apply order.

Test signals: The file has a `before_handle_tasks` failpoint. Behavioral coverage is expected through raftstore-v2 integration tests for committed-entry apply, snapshot generation, manual flush, bucket refresh, and shutdown.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/fsm/apply.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/fsm/mod.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/fsm/mod.rs

Purpose: Defines the FSM module facade for raftstore-v2. It documents the three FSM categories and re-exports the concrete types used by the batch system and other modules.

Important APIs/types/functions: The file declares `mod apply`, `mod peer`, and `mod store`. It re-exports `ApplyFsm`, `ApplyResReporter`, `ApplyScheduler`, `PeerFsm`, `PeerFsmDelegate`, `SenderFsmPair`, `Store`, `StoreFsm`, `StoreFsmDelegate`, and `StoreMeta`.

Control flow: No runtime control flow exists in this module. It is an organizational boundary.

State and persistence behavior: State behavior lives in the submodules. The documentation clarifies that `StoreFsm` handles global control/initialization, `PeerFsm` handles one raft peer, and `ApplyFsm` handles apply tasks for one peer.

Dependencies and integration points: `batch/store.rs`, operation modules, and crate public exports depend on these re-exports. It keeps the internal file layout hidden from callers.

Risks: Re-export churn affects import paths across raftstore-v2. The module categorization is important for maintainability because peer, store, and apply responsibilities are intentionally separated.

Test signals: Compile-time module coverage. Functional validation is in the submodules and integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/fsm/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/fsm/peer.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/fsm/peer.rs

Purpose: Implements the batch-system FSM wrapper for a single raft peer and the delegate that dispatches `PeerMsg` variants into peer/operation logic.

Important APIs/types/functions: `SenderFsmPair` pairs a loose bounded sender with a boxed `PeerFsm`. `PeerFsm` owns `raft::Peer`, an optional mailbox, receiver, tick registry, and stopped flag. `PeerFsm::new` creates the underlying peer and queue. `recv` drains queued `PeerMsg`s into a batch. `Fsm` impl wires mailbox ownership into batch-system. `PeerFsmDelegate` owns temporary mutable access to the FSM and `StoreContext`, with `schedule_tick`, `on_start`, `on_receive_command`, `on_tick`, and `on_msgs`.

Control flow: `on_start` optionally pauses for replay, schedules raft/split/PD/compact ticks, checks merge, starts apply FSM for initialized storage, generates buckets, and wakes leader ready handling. `on_msgs` matches every peer message: raft messages, read/write/admin commands, ticks, apply results, split/merge events, persistence callbacks, snapshot events, bucket refresh, compact log, unsafe recovery, capture changes, and test-only waits. After processing a batch it proposes pending writes, schedules pending ticks, and may acknowledge transfer-leader messages.

State and persistence behavior: The FSM itself stores tick registration and queue state. Persistent effects are delegated to `Peer` methods through raft proposals, state changes, apply scheduling, tablet cleanup, and raft-ready handling. Drop drains pending read/simple-write requests and responds with region-not-found errors to avoid hanging deterministic callbacks.

Dependencies and integration points: It integrates batch-system, raftstore transport/read callbacks, tracker metrics, `StoreContext`, operation modules, `ReplayWatch`, router messages, and the underlying raft peer/storage types.

Risks: `PeerTick::CheckPeerStaleState` and `PeerMsg::Noop` are unimplemented. Missing mailbox for a serving peer causes `slog_panic`. Tick registry correctness prevents duplicate scheduling; failure to clear it would stall ticks. The large message match is a high-change surface where adding new router messages must be reflected here.

Test signals: Assertions cover tick variant count. Integration tests should verify every major `PeerMsg` path, drop responses, tick scheduling, replay start, and leader command latency tracking.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/fsm/peer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/fsm/store.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/fsm/store.rs

Purpose: Implements store-wide FSM state and metadata for raftstore-v2, including read delegates, region range lookup, store ticks, and dispatch for control-plane `StoreMsg`s.

Important APIs/types/functions: `StoreMeta<EK>` tracks `store_id`, read delegates, read progress registry, range index `(region_end_key, epoch.version) -> region_id`, and region initialization state. `set_region` and `remove_region` maintain range metadata with corruption assertions. `StoreRegionMeta` impl exposes store id, read progress, `search_region`, and reader lookup. `Store` tracks store id, last compact checked key, start time, and logger. `StoreFsm` owns `Store` plus a receiver. `StoreFsmDelegate` handles start, tick scheduling, tick dispatch, and message dispatch.

Control flow: On start, the delegate records Unix start time, sends a PD store heartbeat, and schedules cleanup/import-SST and snapshot-GC ticks. `schedule_tick` creates timer futures that force-send `StoreMsg::Tick`. `handle_msgs` dispatches start, ticks, raft messages for unknown peers, split init, store unreachable, merge commit requests, test wait flush, latency inspect, and unsafe recovery store operations.

State and persistence behavior: `StoreMeta` is in-memory authoritative metadata shared behind a mutex. It mirrors persisted region states loaded from raft engine and updated by peer/apply results. Store ticks schedule background actions; actual persistence is delegated to store/peer operation methods and raft engine writes.

Dependencies and integration points: It uses `batch_system::Fsm`, raftstore read progress and store-region traits, TiKV timer helpers, `keys::data_key/data_end_key`, `StoreContext`, and router `StoreMsg`/`StoreTick`. `StorePoller` drives this FSM as the control FSM.

Risks: Region range invariants are protected with asserts and panics, so corrupt metadata can crash the process. Overlapping v2 ranges are handled by including epoch version in the range key; lookup code must consider initialized state and key ordering carefully. Timer tasks are detached through `poll_future_notify`, so send failures are only logged.

Test signals: No local unit tests. Integration should cover region metadata updates/removal, range search with overlapping versions, start idempotency panic, store tick rescheduling, and unknown-peer raft message handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/fsm/store.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/lib.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/lib.rs

Purpose: Defines the crate-level structure and public API for raftstore-v2, TiKV's multi-raft implementation built on batch-system FSMs and operation modules.

Important APIs/types/functions: The file documents the architecture: batch-system threads, FSMs in `fsm`, raft wrapping in `raft`, and operations in `operation`. It enables `box_into_inner`, declares private modules `batch`, `bootstrap`, `fsm`, `operation`, `raft`, and `worker`, plus public `router`. Public re-exports include `StoreRouter`, `StoreSystem`, `create_store_batch_system`, `Bootstrap`, `StoreMeta`, simple-write/state-storage helpers, raftstore `Error/Result/Config`, PD/tablet worker tasks, and `Storage`.

Control flow: There is no runtime control flow. It defines the dependency direction: fields independent of batch-system belong in the raft peer module, while FSM wrappers remain swappable.

State and persistence behavior: Persistence is delegated to operation and raft modules; this file only exposes the types that manipulate it.

Dependencies and integration points: External crates use this root to construct batch systems, bootstrap stores, send router messages, access state storage helpers, and integrate worker tasks. It reuses `raftstore` v1 types such as config and errors.

Risks: Public API exports are stability points for tests and integration. The architecture comments are important: violating the split between `fsm` peer wrappers and underlying raft peer state would make future concurrency changes harder.

Test signals: Compile-time public API coverage and integration tests. No local tests in this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/bucket.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/bucket.rs

Purpose: Implements region bucket interactions for raftstore-v2: refreshing bucket metadata, propagating bucket refreshes to followers, updating read delegates, reporting bucket stats to PD, and triggering approximate bucket generation/split-check work.

Important APIs/types/functions: `Peer::on_refresh_region_buckets` updates local `region_buckets_info`, computes the next bucket version, notifies coprocessors, updates `StoreMeta` read progress, sends `ApplyTask::RefreshBucketStat`, and sends `MsgRefreshBuckets` raft extra messages to non-witness followers when leader. `Peer::on_msg_refresh_buckets` handles follower-side metadata updates. `report_region_buckets_pd`, `maybe_gen_approximate_buckets`, and `gen_bucket_range_for_update` connect bucket stats to PD and split-check. `PeerFsmDelegate::on_report_region_buckets_tick` and `on_refresh_region_buckets` provide message/tick entry points.

Control flow: A refresh request first rejects stale epochs, then updates bucket metadata only if bucket keys/ranges actually change. Leader refreshes are propagated to followers so they flush relevant memtables and update read progress. Periodic report ticks send deltas to the PD worker only when the peer is leader and has bucket stats.

State and persistence behavior: Bucket metadata is mostly in-memory in `region_buckets_info`, read delegates, and apply-side bucket stats. Apply tasks can maintain bucket counters in the apply FSM. The file does not write raft log entries itself; it sends raft extra messages and worker tasks.

Dependencies and integration points: It uses PD `BucketMeta`, raftstore bucket/range/read-progress utilities, coprocessor region change events, split-check tasks, PD worker tasks, `StoreContext`, and `PeerTick::ReportBuckets`.

Risks: Bucket version generation uses the raft term and warns if term exceeds `u32::MAX`, because versions could go backward. Follower refreshes do not update full bucket stats, only read progress metadata. `bucket_stat().unwrap()` assumes refresh produced bucket stats. Stale epoch checks are essential to avoid applying obsolete bucket layouts.

Test signals: No local tests. Integration should cover leader refresh propagation, stale epoch rejection, read delegate updates, PD report scheduling, witness exclusion, and bucket-range split-check generation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/bucket.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/compact_log.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/compact_log.rs

Purpose: Implements raft log compaction and entry-cache eviction for raftstore-v2, including periodic leader decisions, compact-log admin proposals, apply results, raft-engine GC, and tombstone tablet destruction coordination.

Important APIs/types/functions: `CompactLogContext` tracks skipped ticks, approximate log size, last applying index, last compacted index, tombstone tablet indexes waiting for persistence, and an atomic persisted tablet index. `PeerFsmDelegate::on_compact_log_tick` and `on_entry_cache_evict` handle ticks. `Peer::maybe_propose_compact_log` decides compact indexes from applied, first/last, replicated, alive-cache, count/size thresholds, force flag, and skipped tick policy. `propose_compact_log` serializes the admin command. `Apply::apply_compact_log` returns `CompactLogResult`. Peer methods record tombstone tablets, remove them when persisted, handle apply compaction results, advance persisted apply index cleanup, and calculate `compact_log_index`.

Control flow: Leaders periodically schedule compact-log ticks, compact local caches, and propose a compact-log admin request when thresholds are met. Apply returns a compact result without mutating much itself. The peer apply-result handler updates truncated state, persists apply state in `state_changes`, cancels snapshot generation for compacted indexes, schedules raft-engine GC only after persisted apply allows deletion, and adjusts approximate log size. Persisted-apply advancement deletes older raft states and schedules tablet destruction callbacks after safe persistence.

State and persistence behavior: Persistent state changes include apply truncated state, apply-state records, raft-engine GC commands, and cleanup of historical region/apply/flush state records. Tombstone tablet destruction is delayed until replacement tablet indexes are persisted, preventing removal of data still referenced by inflight apply.

Dependencies and integration points: It integrates raftstore config thresholds/metrics, raft-engine `RaftLogBatch`, tablet worker tasks, write-task persisted callbacks, entry storage, merge context, transfer leader cache warmup, and admin command routing.

Risks: Index arithmetic is delicate, including the inherited `compact_idx -= 1` behavior. Assertions require compact indexes below last applying index and no pending tombstone tablets before destroy. Cache warmup can defer compaction. Approximate log size scaling divides by `total_cnt`, so invariants must ensure progress. The TODO notes missing unit tests for compact-log message integrity.

Test signals: Failpoint `maybe_propose_compact_log` exists. Assertions and metrics expose behavior, but local tests are absent. Integration should cover forced compaction, threshold skipping, merge max compact index, persisted-apply cleanup, snapshot cases, and tombstone tablet lifecycle.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/compact_log.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/conf_change.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/conf_change.rs

Purpose: Implements raft configuration-change admin commands for raftstore-v2, covering proposal validation, legacy and v2 apply semantics, region-state mutation, raft-group membership update, PD/coprocessor notification, leader demotion/removal, and GC-peer metadata updates.

Important APIs/types/functions: `ConfChangeResult` captures applied index, raft `ConfChangeV2`, original `ChangePeerRequest`s, and resulting `RegionLocalState`. `UpdateGcPeersResult` carries updated region state. `Peer::propose_conf_change` rejects pending conf changes and serializes either v1 or v2 admin requests. `propose_conf_change_imp` uses `util::check_conf_change`, raft `propose_conf_change`, and metrics. `Peer::on_apply_res_conf_change` applies raft membership, updates storage region state, heartbeats PD, maintains peer heartbeat records, updates `StoreMeta`, read progress, and coprocessor events. `Apply::apply_conf_change`, `apply_conf_change_v2`, `apply_conf_change_imp`, `apply_leave_joint`, `apply_single_change_legacy`, `apply_single_change`, and `apply_update_gc_peer` perform apply-side region mutations.

Control flow: Proposal validates raft health and config rules, then raft proposes a sync-log conf change. Apply-side code determines simple/enter-joint/leave-joint kind, mutates peer roles and peer lists, advances conf version, records removed peers, tombstones self if removed, and returns an admin result. Peer-side result handling applies raft conf change when the log is still present, persists the new region state unless self is removed, and may step down if the leader is removed or demoted.

State and persistence behavior: Region metadata, peer roles, epoch conf version, removed/merged records, and tombstone state are persisted through region-state writes. In-memory raft membership, store meta, read progress, peer heartbeat maps, and coprocessor region-change notifications are synchronized with that persisted state.

Dependencies and integration points: It uses raft `ConfChangeV2`, raftstore utility validation, admin metrics, coprocessor region events, `StoreContext`, and underlying `Apply`/`Peer` region-state APIs.

Risks: Joint consensus transitions are complex; applying changes while still in joint state can panic. Duplicate same-store peers and mismatched removals are rejected. Proposal can be silently dropped by raft; this is mapped to `NotLeader`. Leader self-demotion/removal must step down promptly. Failpoints and TODOs indicate areas needing stronger coverage.

Test signals: Failpoint `apply_on_add_node_1_2` and comments around pending tests. Crate integration tests should cover v1/v2 changes, enter/leave joint, add learner/promote/demote/remove, self removal, redundant PD changes, and GC-peer record cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/conf_change.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/flashback.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/flashback.rs

Purpose: Implements prepare/finish flashback admin commands for raftstore-v2, toggling region flashback state and coordinating pessimistic lock behavior.

Important APIs/types/functions: `FlashbackResult` carries applied index and resulting `RegionLocalState`. `Peer::propose_flashback` serializes and proposes the admin request. `Apply::apply_flashback` handles `AdminCmdType::PrepareFlashback` and `FinishFlashback`, updates region `is_in_flashback` and `flashback_start_ts`, updates `PEER_ADMIN_CMD_COUNTER` and `PEER_IN_FLASHBACK_STATE`, and returns `AdminCmdResult::Flashback`. `Peer::on_apply_res_flashback` updates store metadata, read delegate/peer region state, persists region state, and updates pessimistic lock status.

Control flow: Proposal is a normal raft proposal. Apply toggles flashback fields in the in-memory apply region state and reports the result. Peer result handling optionally mutates state via failpoint, writes the region into `StoreMeta`, calls `set_region` with `RegionChangeReason::Flashback`, records a region-state write in `state_changes`, and adjusts pessimistic lock status based on flashback and leadership.

State and persistence behavior: Persistent state is the `RegionLocalState` written at the applied index. In-memory state includes store metadata, read delegate region, peer region, flashback metrics, and pessimistic lock table status. Entering flashback clears existing pessimistic locks and blocks new ones with `LocksStatus::IsInFlashback`.

Dependencies and integration points: It uses raftstore admin metrics, `LocksStatus`, coprocessor region-change reason, `StoreContext`, `ApplyResReporter`, and peer transaction context locks. It mirrors v1 behavior but notes v2 does not expire a remote lease because only local readers serve reads.

Risks: `meta.readers.get_mut(&region_id).unwrap()` assumes a reader exists for the region. Metrics must stay balanced across prepare/finish, especially repeated commands. The failpoint can simulate a peer FSM state mismatch. Lock status transitions depend on leadership after leaving flashback.

Test signals: Failpoint `keep_peer_fsm_flashback_state_false` exists. Integration should cover prepare/finish idempotence, metric gauge balance, lock clearing/blocking, follower lock status, and persistence of flashback start timestamp.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/flashback.rs -->
