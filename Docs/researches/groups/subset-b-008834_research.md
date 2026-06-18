# Research Group: subset-b-008834

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/health_controller/src/lib.rs -->
# sources/storage-engines/tikv/components/health_controller/src/lib.rs

Purpose: defines the shared `HealthController` facade for TiKV process health, plus the internal state that backs raftstore slow score, raftstore slow trend, network latency retrieval, and gRPC health-service status. It centralizes the distinction between process serving state and module-level unhealthy state.

Important APIs/types/functions: `HealthChecker` abstracts raft-client/network latency providers as `store_id -> max_latency_ms`; `HealthControllerInner` owns `raftstore_slow_score`, `raftstore_slow_trend`, `health_checker`, `health_service`, and `current_serving_status`; `HealthController` exposes `new`, `set_health_checker`, slow-score/trend getters, `get_grpc_health_service`, `get_serving_status`, `set_is_serving`, and `shutdown`. `RollingRetriever<T>` is a double-buffered RwLock helper used to publish protobuf trend values without blocking readers on writes.

Control flow: initialization creates a gRPC `HealthService` set to `NotServing`, slow score defaults to `1.0`, and slow trend defaults through `RollingRetriever`. `set_is_serving` updates `ServingStatus` under a mutex and mirrors it into gRPC. Reporters call private `add_unhealthy_module`/`remove_unhealthy_module`; when serving and the unhealthy set transitions between empty and non-empty, gRPC status flips between `Serving` and `ServiceUnknown`. `get_network_latencies` locks the optional checker and converts millisecond floats to `Duration`.

State and persistence: all state is in-memory and process-local. Slow score is stored as `f64::to_bits` in an `AtomicU64` with release/acquire ordering. Trend data is in two RwLock slots plus an atomic active index. Health-service status consistency relies on updating gRPC while holding `current_serving_status`.

Dependencies/integration: integrates with `grpcio_health`, `kvproto::pdpb::SlowTrend`, `parking_lot`, `collections::HashMap`, and the reporter modules. Raftstore reporters publish values through `HealthControllerInner`; external services consume gRPC health and public getters.

Risks: `Duration::from_millis(latency_ms as u64)` truncates fractional latency and silently saturates semantic precision; `HealthChecker` is under a mutex and can block health reads if its implementation is slow; `RollingRetriever` intentionally sacrifices read/write linearizability, so callers must tolerate stale trend snapshots.

Test signals: unit tests cover serving-state transitions with multiple unhealthy modules and `RollingRetriever` behavior, including nonblocking reads during writes and serialization of concurrent writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/health_controller/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/health_controller/src/reporters.rs -->
# sources/storage-engines/tikv/components/health_controller/src/reporters.rs

Purpose: implements reporters that convert raftstore latency observations into health-controller state: disk/network slow scores, slow-trend protobufs, and module unhealthy markers.

Important APIs/types/functions: `RaftstoreReporterConfig` carries tick intervals, trend sensitivity knobs, network weighting, and Prometheus gauges. `UnifiedSlowScore` owns disk `SlowScore`s and per-store network `SlowScore`s. `RaftstoreReporter` records durations, ticks factors, publishes aggregate disk score, records network latencies from `HealthChecker`, updates slow trend, and toggles raftstore health. `SlowTrendStatistics` holds the cause/result `Trend`s and request-per-second recorder. `TestReporter` directly sets slow score for tests.

Control flow: `UnifiedSlowScore::new` creates two disk factors for raft disk and KvDB disk. Disk `record_duration` records trend cause data, records disk duration with the selected `InspectFactor`, and publishes max disk score. Network recording pulls current latencies from the controller and updates one `SlowScore` per remote store, removing stale store IDs. `tick_network` synchronizes all per-store tick IDs, ticks each factor, and reports an average only when every factor produced an update. Disk `tick` handles unfinished prior ticks as timeouts when the store is not busy, recovers health when all disk ticks finish, marks raftstore unhealthy when a score update has no new record, and publishes updated disk score.

State and persistence: all scores/trends are in-memory. Network factors sit behind `Arc<Mutex<HashMap<u64, SlowScore>>>`; disk factors are local to the reporter. The durable side effect is limited to publishing into `HealthControllerInner` and Prometheus metrics updates inside trend internals.

Dependencies/integration: depends on `slow_score`, `trend`, `types::InspectFactor`, `kvproto::pdpb::SlowTrend`, and `prometheus::IntGauge`. It is expected to be ticked externally by the PD worker rather than spawning its own timer.

Risks: incorrect tick-ID synchronization would misattribute network samples; network score conversion to `u64` truncates; disk health can become `ServiceUnknown` when inspections stop producing records even if actual I/O is unknown rather than bad. `std::sync::Mutex` is used for network factors, so poisoned locks panic through `unwrap`.

Test signals: tests cover network factor creation/removal, tick-ID synchronization, score update cadence, timeout-driven score growth, and recovery under normal durations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/health_controller/src/reporters.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/health_controller/src/slow_score.rs -->
# sources/storage-engines/tikv/components/health_controller/src/slow_score.rs

Purpose: defines the AIMD slow-score algorithm used by health reporters to summarize repeated timeout observations into a score in `[1, 100]`.

Important APIs/types/functions: constants define disk/network recovery intervals, round tick sizes, timeout-ratio thresholds, and network timeout threshold. `SlowScore::new` builds a score with explicit timeout threshold, tolerated ratio, round tick count, and recovery interval. `new_with_extra_config` derives KvDB-specific round ticks from inspect interval. `record`, `record_timeout`, `tick`, `update`, `should_force_report_slow_store`, and tick-ID accessors are the main API. `SlowScoreTickResult` reports tick ID, optional updated score, whether a new record was observed, and force-report signal.

Control flow: `record` only accepts a sample when its ID matches `last_tick_id`, then marks the tick finished, increments total requests, and counts a timeout if the store is not busy and duration exceeds threshold. `tick` advances the tick ID, marks the new tick unfinished, and updates the score only every `round_ticks`. `update_impl` decreases score linearly toward `1.0` when there were no timeouts, or increases multiplicatively based on timeout ratio clamped by the configured threshold.

State and persistence: state is in-memory counters and timestamps (`last_record_time`, `last_update_time`). `OrderedFloat<f64>` enables comparisons and arithmetic around the score and threshold.

Dependencies/integration: consumed by `UnifiedSlowScore` in `reporters.rs`; depends on `ordered_float` and standard `Instant`/`Duration`.

Risks: if `timeout_requests > 0` while `total_requests == 0`, timeout ratio would divide by zero, though current call paths increment both together. Tick-ID mismatches silently drop records. Recovery amount uses elapsed wall-clock duration since last update, so scheduling delays can accelerate score decrease.

Test signals: unit tests validate multiplicative increases, linear recovery to one, KvDB extra config behavior, and minimum one tick for long inspect intervals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/health_controller/src/slow_score.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/health_controller/src/trend.rs -->
# sources/storage-engines/tikv/components/health_controller/src/trend.rs

Purpose: implements rolling-window trend detection for slow causes and slow results, including sample windows, history baselines, optional spike filtering, and composed increasing-rate signals.

Important APIs/types/functions: `SampleWindow` records timestamped values, sum, overflow flag, average, standard deviation, and drain/move helpers. `SampleWindows` records into L0/L1/L2 windows. `HistoryWindow` samples historical averages, tracks previous/current history windows, computes margin error, and flips history during sustained regime changes. `SpikeFilter` suppresses short high spikes after history is established. `Trend` exposes `record`, `increasing_rate`, `l0_avg`, `l1_avg`, `l2_avg`, margin-error base accessors, and L0/L1 and L1/L2 rate calculations. `RequestPerSecRecorder` converts observed request count deltas into RPS.

Control flow: `Trend::record` applies sample-interval gating, bypasses spike filtering until enabled and L1 has overflowed, then records filtered or unfiltered samples into all data windows. Each unfiltered sample updates history windows using the current composed increasing rate. Rate calculation waits until L2 and relevant history are valid, subtracts margin error, preserves sign, and scales by current average and baseline. History flipping starts when current values diverge beyond margin and ends after the changing phase stabilizes.

State and persistence: all data is in-memory `VecDeque` samples and gauges. Overflow indicates that a window has enough age to be treated as a baseline. Prometheus gauges record filter activity and history gap seconds.

Dependencies/integration: used by `SlowTrendStatistics` in `reporters.rs`; depends on `prometheus::IntGauge` and `tikv_util::info`.

Risks: algorithms are heuristic and sensitive to duration/sensitivity constants. `Instant::duration_since` is used in several paths, with comments acknowledging time adjustment concerns in flipping. Spike filter is disabled in current reporter config by zero duration, so that path may receive less production exercise.

Test signals: unit test covers `SampleWindow` validity, averages, overflow, and standard-deviation ratio; higher-level reporter tests exercise trend publishing but not the full flipping/filtering matrix.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/health_controller/src/trend.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/health_controller/src/types.rs -->
# sources/storage-engines/tikv/components/health_controller/src/types.rs

Purpose: defines common latency data types and inspection factors shared by the health-controller reporters and raftstore instrumentation.

Important APIs/types/functions: `RaftstoreDuration` stores optional durations for store wait/process/write/commit and apply wait/process stages. `sum`, `delays_on_disk_io`, and `delays_on_net_io` classify latency into disk and network components. `InspectFactor` identifies `RaftDisk`, `KvDisk`, and `Network`, with `as_str` labels. `LatencyInspector` accumulates stage durations and invokes a one-shot callback on `finish`.

Control flow: instrumentation creates a `LatencyInspector` with an ID and callback, calls record methods as raftstore stages complete, and finally consumes it with `finish`, passing the collected `RaftstoreDuration`. Reporters later derive disk/network delays from optional fields, treating missing stages as zero.

State and persistence: state is transient per inspection. There is no persistence, shared synchronization, or background work.

Dependencies/integration: exported from `lib.rs` and used by reporters and raftstore latency inspection paths. The callback signature bridges instrumentation to reporter recording.

Risks: missing duration fields default to zero, so incomplete instrumentation can underreport latency. Comments contain spelling mistakes but no behavioral effect. `InspectFactor` discriminants are used as vector indices in reporters, so adding/reordering variants requires updating factor-vector layout.

Test signals: no direct tests in this file; behavior is indirectly covered by reporter slow-score and trend tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/health_controller/src/types.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/Cargo.toml -->
# sources/storage-engines/tikv/components/hybrid_engine/Cargo.toml

Purpose: declares the `hybrid_engine` crate, a non-published TiKV workspace crate that composes RocksDB and region-cache/in-memory engine behavior.

Important APIs/types/functions: package metadata sets edition 2024 and Apache-2.0 licensing. Runtime dependencies include `engine_traits`, `engine_rocks`, `in_memory_engine`, `raftstore`, `kvproto`, `keys`, `txn_types`, `prometheus`, `prometheus-static-metric`, `protobuf`, `online_config`, `tikv_util`, and `tempfile`. Dev dependencies add `fail`, `test_util`, and `tempfile`.

Control flow: no executable control flow; the manifest wires compile-time integration and test-only failpoint support.

State and persistence: no runtime state. Dependency choices imply interaction with persistent RocksDB and in-memory region cache through source modules.

Dependencies/integration: sits between storage engine traits, RocksDB implementation, in-memory cache implementation, and raftstore coprocessor observers. Prometheus dependencies support hybrid snapshot/cache metrics.

Risks: duplicate `tempfile` appears in both normal and dev dependencies; because test utilities are exported from `src/util.rs`, normal `tempfile` may be intentional. Edition 2024 requires toolchain support across the workspace.

Test signals: dev dependencies and crate tests in source files rely on failpoints, `test_util`, and temporary RocksDB instances.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/db_vector.rs -->
# sources/storage-engines/tikv/components/hybrid_engine/src/db_vector.rs

Purpose: wraps values returned from either disk snapshots or region-cache snapshots behind one `DbVector` type.

Important APIs/types/functions: `HybridDbVector<EK, EC>` stores `Either<disk DbVector, cache DbVector>`. `try_from_disk_snap` and `try_from_cache_snap` call `get_value_cf_opt` on the selected snapshot and wrap present values. It implements `DbVector`, `Deref<Target=[u8]>`, `Debug`, and `PartialEq<&[u8]>`.

Control flow: snapshot peek code chooses disk or cache; this module only performs the chosen read and preserves which engine produced the value. Deref and debug dispatch on `Either`.

State and persistence: the wrapper owns the engine-specific vector returned by a snapshot. It does not mutate or persist data.

Dependencies/integration: used by `HybridEngineSnapshot` as its `Peekable::DbVector`; depends on `engine_traits` and `tikv_util::Either`.

Risks: equality implementation is only for `&[u8]`, not symmetric with all byte containers. Any lifetime/copy semantics depend on the underlying engine-specific `DbVector` implementations.

Test signals: indirectly exercised by hybrid snapshot and write-to-both-engines tests that call `get_value`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/db_vector.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/engine.rs -->
# sources/storage-engines/tikv/components/hybrid_engine/src/engine.rs

Purpose: defines the `HybridEngine` container holding a complete disk `KvEngine` plus a selective `RegionCacheEngine`.

Important APIs/types/functions: `HybridEngine<EK, EC>` stores `disk_engine` and `region_cache_engine`, with `new` and `region_cache_engine` accessors. Test-only helpers include `new_snapshot`, `disk_engine`, and `SnapshotContext`.

Control flow: test snapshot creation always takes a disk snapshot; if the cache engine is enabled and a context is supplied, it attempts to acquire a cache snapshot using region, read timestamp, and disk sequence number. Failed cache acquisition falls back to disk-only snapshot.

State and persistence: the struct owns cloneable engine handles. Disk persistence belongs to `EK`; cache residency and safe points belong to `EC`.

Dependencies/integration: generic over `engine_traits::KvEngine` and `RegionCacheEngine`; exported by `lib.rs` and used by tests/utilities.

Risks: production snapshot acquisition appears handled by raftstore snapshot observers rather than this test-only helper. The helper unwraps `ctx.region`, so malformed test context panics.

Test signals: `test_engine` verifies cache snapshot availability depends on context, safe point/read_ts, and dynamic config disabling the in-memory engine.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/engine.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/engine_iterator.rs -->
# sources/storage-engines/tikv/components/hybrid_engine/src/engine_iterator.rs

Purpose: provides a single iterator and metrics collector facade over disk and region-cache snapshot iterators.

Important APIs/types/functions: `HybridEngineIterator<EK, EC>` stores `Either<disk iterator, cache iterator>`. Constructors create disk or cache variants. It implements all `engine_traits::Iterator` operations by dispatching to the inner iterator. `HybridEngineIterMetricsCollector` wraps either underlying collector and implements `IterMetricsCollector`. `MetricsExt` returns the appropriate collector.

Control flow: `HybridEngineSnapshot::iterator_opt` selects which constructor to use; subsequent seek/next/prev/key/value/valid calls are pure dispatch.

State and persistence: iterator state lives inside the selected underlying engine iterator. The wrapper does not persist data.

Dependencies/integration: integrates `engine_traits::{Iterable, Iterator, MetricsExt, IterMetricsCollector}` with `tikv_util::Either`.

Risks: metrics are only from the selected engine, so higher-level consumers must know that a hybrid iterator is not aggregating both engines. Any non-data CF fallback behavior is controlled in snapshot selection, not here.

Test signals: snapshot iterator test verifies cache-backed iteration returns a value written through the hybrid write-batch observer.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/engine_iterator.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/lib.rs -->
# sources/storage-engines/tikv/components/hybrid_engine/src/lib.rs

Purpose: crate root for the hybrid engine shim.

Important APIs/types/functions: declares internal modules `db_vector`, `engine`, `engine_iterator`, `metrics`, `snapshot`, `util`, and public module `observer`. Re-exports `HybridEngine` and `HybridEngineSnapshot`.

Control flow: no runtime control flow. The TODO notes the crate has become thin and may be folded into `in_memory_engine`.

State and persistence: no state in this file.

Dependencies/integration: defines the crate’s public surface for consumers needing hybrid engine construction, snapshots, and observers.

Risks: because most modules are private, consumers rely on the re-exported types and public observer module; moving this crate would require updating import paths across raftstore/storage integration.

Test signals: no direct tests; all module tests compile through this root.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/metrics.rs -->
# sources/storage-engines/tikv/components/hybrid_engine/src/metrics.rs

Purpose: defines Prometheus counters for hybrid snapshot selection, in-memory snapshot acquisition failures, and transfer-leader cache warmup behavior.

Important APIs/types/functions: static-metric label enums include `SnapshotType` (`rocksdb`, `in_memory_engine`, `wasted`), `FailedReason` (`no_read_ts`, `not_cached`, `too_old_read`, `epoch_not_match`), and `TransferLeaderWarmupType` (`request`, `warmup`, `skip_warmup`). Lazy statics register `IntCounterVec`s and auto-flush static wrappers.

Control flow: metric registration happens lazily. Observers increment static counters during snapshot pin take/drop and transfer leader warmup paths.

State and persistence: Prometheus counters are process-local metrics, reset on restart and exported through TiKV metrics infrastructure.

Dependencies/integration: used by `observer/snapshot.rs` and `observer/load_eviction.rs`; depends on `lazy_static`, `prometheus`, and `prometheus-static-metric`.

Risks: typo in exported `IN_MEMORY_ENGINE_SNAPSHOT_ACQUIRE_FAILED_REASON_COUNT_STAIC` is part of the source API. `no_read_ts` label is defined but not used in the read code here, which may indicate either future use or incomplete accounting.

Test signals: no direct metric tests; observer tests exercise paths but do not assert counter values.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/observer/load_eviction.rs -->
# sources/storage-engines/tikv/components/hybrid_engine/src/observer/load_eviction.rs

Purpose: implements raftstore coprocessor observers that keep the region cache correct across raft apply events, role changes, peer destruction, snapshots, and transfer-leader warmup.

Important APIs/types/functions: `LoadEvictionObserver` owns an `Arc<dyn RegionCacheEngineExt + Send + Sync>`. `register_to` registers query, admin, apply-snapshot, role, destroy-peer, and transfer-leader observers. Helpers emit `RegionEvent::{Split, Eviction, TryLoad, EvictByRange}`. Transfer-leader handling uses custom context key `b"ime"` and `ExtraMessageType::MsgPreLoadRegionRequest`.

Control flow: query pre-exec evicts by delete range. Post-exec command evicts on ingest SST and prepare merge, evicts then reloads on commit/rollback merge, and sends split events without evicting hot split regions. Admin pre-exec evicts on prepare flashback. Applying a snapshot evicts the region. Becoming leader triggers manual-range load attempts; initialized follower transition evicts. Destroying a peer evicts, inserting a dummy peer for uninitialized regions to avoid `CacheRegion::from_region` panic. Transfer-leader pre-hook requests warmup when the source region is cached; transferee ack hook loads the region and delays ack until active cache exists.

State and persistence: no persistent state in the observer. It translates raftstore events into cache engine events; cache state and disk data live elsewhere. Warmup metrics are incremented.

Dependencies/integration: integrates deeply with `raftstore::coprocessor`, `engine_traits::RegionCacheEngineExt`, `kvproto`, `raft`, `keys`, and `tikv_util` logging/varint decoding.

Risks: event ordering is critical for cache correctness. Merge reload is asynchronous through `on_evict_finished`; failure or delay can reduce hit ratio. Compatibility fallback in transfer-leader ack returns ready on invalid/missing context, preserving availability but skipping warmup.

Test signals: tests use a mock region cache engine to verify no eviction on split, eviction on ingest SST, and try-load when becoming leader.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/observer/load_eviction.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/observer/mod.rs -->
# sources/storage-engines/tikv/components/hybrid_engine/src/observer/mod.rs

Purpose: module hub for hybrid engine raftstore observers.

Important APIs/types/functions: declares `load_eviction`, `snapshot`, `write_batch`, and test-only `test_write_batch`. Re-exports `LoadEvictionObserver`, `HybridSnapshotObserver`, `RegionCacheSnapshotPin`, and `RegionCacheWriteBatchObserver`.

Control flow: no runtime control flow; it organizes observer APIs for crate consumers.

State and persistence: no state.

Dependencies/integration: provides public imports used when registering hybrid engine observers with raftstore coprocessor host.

Risks: observer modules are tightly coupled to raftstore coprocessor traits; public re-exports form a small compatibility surface if modules move.

Test signals: test-only module is included under `cfg(test)` and contains write-batch integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/observer/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/observer/snapshot.rs -->
# sources/storage-engines/tikv/components/hybrid_engine/src/observer/snapshot.rs

Purpose: pins in-memory region-cache snapshots during raftstore snapshot observation and accounts for cache-vs-RocksDB snapshot usage.

Important APIs/types/functions: `RegionCacheSnapshotPin` stores `Option<Result<RegionCacheSnapshot, FailedReason>>`, implements `ObservedSnapshot`, increments `wasted` if dropped with an unused successful snapshot, and exposes `take`. `HybridSnapshotObserver` owns a `RegionCacheMemoryEngine`, registers as a `SnapshotObserver`, and returns snapshot pins from `on_snapshot`.

Control flow: when raftstore takes a snapshot, the observer converts the region to `CacheRegion` and calls `cache_engine.snapshot(region, read_ts, sequence_number)`. Later, `HybridEngineSnapshot::from_observed_snapshot` downcasts and calls `take`; success increments `in_memory_engine`, known failures increment failure reason and `rocksdb`, and absence returns `None`.

State and persistence: snapshot pins hold cache snapshot references to prevent eviction/deletion while the raftstore snapshot is live. Metrics are process-local.

Dependencies/integration: integrates `in_memory_engine::{RegionCacheMemoryEngine, RegionCacheSnapshot}`, `engine_traits::{CacheRegion, FailedReason}`, raftstore `ObservedSnapshot`/`SnapshotObserver`, and hybrid metrics.

Risks: downcast in `HybridEngineSnapshot` uses `unwrap`, so observed snapshot type must match. Unused successful pins count as wasted, which is useful but can reveal over-acquisition outside coprocessor reads.

Test signals: indirect tests in hybrid engine snapshot paths validate cache snapshot acquisition/fallback behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/observer/snapshot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/observer/test_write_batch.rs -->
# sources/storage-engines/tikv/components/hybrid_engine/src/observer/test_write_batch.rs

Purpose: integration-style tests for the hybrid observable write batch and its interaction with disk writes, in-memory cache writes, sequence numbers, loading regions, and range deletion eviction.

Important APIs/types/functions: tests use `hybrid_engine_for_tests`, `RegionCacheWriteBatchObserver`, raftstore `WriteBatchWrapper`, `CacheRegion`, `RegionCacheEngine`, and in-memory internal key decoding. Failpoints pause loading to verify sequence behavior.

Control flow: `test_sequence_number_unique` writes initial data, starts loading overlapping regions, blocks one load, then writes puts/deletes across prepared regions and verifies internal key order and sequence numbers. `test_write_to_both_engines` writes through a wrapped batch and reads from disk, hybrid snapshot, and cache snapshot. `test_set_sequence_number` verifies setting sequence twice fails. `test_delete_range` writes data to two regions, verifies cache snapshots exist, deletes ranges, and waits until affected cache data is evicted.

State and persistence: tests create temporary RocksDB and in-memory engines. They validate that disk persistence and cache mutation happen together through the wrapper while cache eviction is asynchronous for range deletion.

Dependencies/integration: depends on failpoints, crossbeam epoch, in-memory engine internals, raftstore write-batch wrapper, and test utilities.

Risks: tests rely on internal key ordering and failpoint names; those are strong regression signals but can be brittle during refactors. Eventual eviction uses timing-based waiting.

Test signals: this file itself is the primary regression suite for hybrid write-batch correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/observer/test_write_batch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/observer/write_batch.rs -->
# sources/storage-engines/tikv/components/hybrid_engine/src/observer/write_batch.rs

Purpose: implements a raftstore write-batch observer that mirrors relevant data-CF mutations into the region cache.

Important APIs/types/functions: `RegionCacheWriteBatchObserver` owns a `RegionCacheMemoryEngine`, registers as `WriteBatchObserver`, and creates `HybridObservableWriteBatch`. `HybridObservableWriteBatch` wraps `RegionCacheWriteBatch`, implements `ObservableWriteBatch`, `WriteBatch`, and `Mutable`.

Control flow: raftstore asks the observer for an observable batch. `prepare_for_region` forwards region context; `write_opt_seq` sets the cache batch sequence number then writes it with the same options; `post_write` compacts lock CF if needed. Mutations delegate to cache batch, except `put_cf` filters to data CFs. Range deletes are forwarded because cache interprets them as eviction of overlapping regions.

State and persistence: disk persistence is handled by the main write batch wrapper; this observer mutates in-memory region cache state. Sequence numbers align cache MVCC ordering with disk write sequence.

Dependencies/integration: integrates `engine_traits::{WriteBatch, Mutable, is_data_cf}`, `in_memory_engine::RegionCacheWriteBatch`, and raftstore coprocessor observable write batches.

Risks: several `WriteBatch` methods are intentionally `unimplemented!` because raftstore only uses the boxed observable interface; accidental direct use would panic. `write_opt_seq` unwraps cache sequence/write results, so cache write failure panics rather than propagating.

Test signals: covered by `test_write_batch.rs` for sequence uniqueness, writing to both engines, duplicate sequence setting, and delete-range eviction.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/observer/write_batch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/snapshot.rs -->
# sources/storage-engines/tikv/components/hybrid_engine/src/snapshot.rs

Purpose: implements `HybridEngineSnapshot`, which routes reads to the region cache when a cache snapshot is available and the column family is data-bearing, otherwise to the disk snapshot.

Important APIs/types/functions: `HybridEngineSnapshot::new`, `region_cache_snapshot_available`, `region_cache_snap`, and `disk_snap` expose snapshot parts. `from_observed_snapshot` converts raftstore observed snapshot pins into `RegionCacheMemoryEngine` cache snapshots. Trait impls cover `Snapshot`, `Debug`, `Iterable`, `Peekable`, `CfNamesExt`, and `SnapshotMiscExt`.

Control flow: iterators and point reads check `region_cache_snap()` and `is_data_cf(cf)`. Data CF reads use cache; non-data CFs and cache misses/fallback snapshots use disk. `from_observed_snapshot` downcasts an observed snapshot pin, takes the cache snapshot, and stores it as optional.

State and persistence: owns a disk snapshot and optional cache snapshot. The snapshot is read-only and preserves disk sequence number through `SnapshotMiscExt`.

Dependencies/integration: uses `HybridDbVector`, `HybridEngineIterator`, `RegionCacheSnapshotPin`, `engine_traits`, `in_memory_engine::RegionCacheMemoryEngine`, and raftstore observed snapshots.

Risks: downcast unwrap assumes only the expected snapshot observer contributes pins. Routing all data CF reads to cache when available assumes the cache snapshot is complete and valid for the target region/read_ts. Non-data CFs always hit disk.

Test signals: `test_iterator` verifies cache-backed iteration after a write through the observable write batch.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/snapshot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/util.rs -->
# sources/storage-engines/tikv/components/hybrid_engine/src/util.rs

Purpose: provides a test utility to create a temporary hybrid engine backed by RocksDB and a `RegionCacheMemoryEngine`.

Important APIs/types/functions: `hybrid_engine_for_tests` accepts a temp-dir prefix, `InMemoryEngineConfig`, and a configuration closure. It returns `(TempDir, HybridEngine<RocksEngine, RegionCacheMemoryEngine>)`.

Control flow: the helper creates a temp directory, opens RocksDB with default/lock/write CFs, creates an in-memory engine with test context and config `VersionTrack`, connects the disk engine into the memory engine, runs the caller configuration closure, and returns the hybrid engine.

State and persistence: persistence is temporary filesystem RocksDB scoped by `TempDir`; cache state is configured in-memory by the closure.

Dependencies/integration: used by hybrid engine tests; depends on `engine_rocks`, `engine_traits`, `in_memory_engine`, `tempfile`, and `tikv_util::config::VersionTrack`.

Risks: intended for tests despite being in public `util`; misuse in production would create temporary storage. The closure runs after disk engine attachment, allowing test setup of regions and safe points.

Test signals: doctest-style example shows region creation; many module tests use this helper.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/hybrid_engine/src/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/Cargo.toml -->
# sources/storage-engines/tikv/components/in_memory_engine/Cargo.toml

Purpose: declares the `in_memory_engine` crate, including features, tests, benchmark, and dependencies for TiKV’s region cache memory engine.

Important APIs/types/functions: features include `testexport` and `failpoints`. A failpoints test target is gated by the `failpoints` feature. A Criterion benchmark named `load_region` points to `benches/load_region.rs`. Dependencies include concurrency/data structures (`crossbeam`, `crossbeam-skiplist`, `dashmap`, `parking_lot`), engine integration (`engine_traits`, `engine_rocks`), raftstore, PD/security/config utilities, Prometheus metrics, Tokio/yatp, and MVCC-related crates.

Control flow: no runtime control flow; manifest controls compilation of production code, failpoint tests, and benchmark harness.

State and persistence: no direct state; dependencies indicate the crate bridges in-memory state with disk engine snapshots and raftstore events.

Dependencies/integration: consumed by `hybrid_engine` and likely raftstore/storage code. Dev dependencies support Criterion benchmarks, property tests, temp RocksDB, test PD, and jemalloc allocation tests.

Risks: failpoint dependency is both normal and feature-gated, so production build configuration needs care. Edition 2024 and broad workspace dependencies tie this crate closely to the full TiKV workspace.

Test signals: manifest exposes failpoint tests and the load-region benchmark, indicating correctness and performance coverage around background loading.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/benches/load_region.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/benches/load_region.rs

Purpose: Criterion benchmark for background region loading from RocksDB into the in-memory region cache under varying value sizes.

Important APIs/types/functions: `bench_load_region` iterates value sizes `[32, 128, 512, 4096]`; `bench_with_args` configures Criterion group and calls `load_region`; `prepare_data` creates MVCC-like RocksDB data in default/write CFs; `load_region` constructs `RegionCacheMemoryEngine`, `BackgroundRunner`, marks a region loading, and runs `worker.run_load_region`; `MockTsPdClient` returns a fixed large timestamp.

Control flow: data preparation creates random keys with variable MVCC version amplification, writes short values inline in write records and larger values to default CF, then benchmarks loading the full data key range. `load_region` attaches the disk engine, creates a memory controller and background runner, requests region load, forces state to `Loading` to avoid duplicate background load, and invokes the runner directly with a disk snapshot.

State and persistence: uses a temporary RocksDB containing generated benchmark data and a fresh in-memory engine per iteration. The benchmark intentionally drops large loaded state after each iteration.

Dependencies/integration: depends on `criterion`, Rocks engine utilities, `engine_traits`, futures `ready`, PD client trait, raftstore split size, random generation, TiKV config `VersionTrack`, and MVCC `txn_types`.

Risks: random data makes benchmark inputs realistic but less deterministic at the byte-pattern level. Warm-up time and sample size are intentionally small because workload is slow, trading statistical rigor for practical runtime.

Test signals: not a test but a performance signal for region cache background loading across value sizes and MVCC amplification.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/benches/load_region.rs -->
