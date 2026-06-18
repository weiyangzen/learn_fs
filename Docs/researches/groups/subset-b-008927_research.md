# subset-b-008927 Research

Grouped source research for TiKV server engine factory and GC worker files. Each section is source-tree aligned and can be split into the required per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/engine_factory.rs -->
# sources/storage-engines/tikv/src/server/engine_factory.rs

## Purpose

This file builds TiKV KV RocksDB engines for both shared RaftKV and per-region tablet RaftKV2 layouts. It centralizes RocksDB option construction, column-family option construction, event listener wiring, tablet creation, tablet destruction, and the state-persistence listener used when WAL is disabled in v2. It is the bridge between `TikvConfig`/RocksDB resources and `engine_traits::TabletFactory<RocksEngine>`.

## Important APIs, Types, And Functions

- `FactoryInner` stores shared immutable construction inputs: `RegionInfoAccessor`, `DbConfig`, API version, flow listener, SST recovery scheduler, encryption key manager, shared DB/CF resources, optional `StateStorage`, and `lite` mode.
- `KvEngineFactoryBuilder::new` derives RocksDB and CF resources from `TikvConfig`, cache, Rocks env, and force-partition range manager.
- Builder setters install region metadata, flow listener, SST recovery scheduler, compaction-event sender, lite mode, and v2 state storage.
- `KvEngineFactory::create_raftstore_compaction_listener` creates a `CompactionListener` only when a compacted-event sender exists, and filters compaction events to write/default CF output levels >= 2 for region-size accounting.
- `db_opts` builds `RocksDbOptions` and, outside lite mode, adds the generic Rocks event listener plus the raftstore compaction listener.
- `cf_opts` delegates to `DbConfig::build_cf_opts`, optionally with a `RangeCompactionFilterFactory` for tablets.
- `create_shared_db` opens `path/DEFAULT_ROCKSDB_SUB_DIR` as a RaftKv engine.
- `TabletFactory<RocksEngine>` implementation opens/destroys tablets and checks existence.

## Control Flow

Shared DB creation builds RaftKv DB options and CF options without a range compaction filter, attaches the flow listener if configured, then opens RocksDB under the configured RocksDB subdirectory. Tablet creation builds RaftKv2 DB options, changes the info log to a tablet-specific `TabletLogger`, creates a `RangeCompactionFilterFactory` from the tablet context start/end keys, attaches tablet-specific flow and persistence listeners, and opens the database at the tablet path. On success it notifies the flow listener with `on_created`; destruction logs the tablet identity, trashes the tablet directory with encryption-aware deletion, and notifies `on_destroyed`.

## State And Persistence Behavior

Most factory state is held behind `Arc<FactoryInner>` and cloned into factory instances. Shared RocksDB resources and CF resources are constructed once in the builder and reused by later opens. When `state_storage` and `ctx.flush_state` are present, `open_tablet` installs `RocksPersistenceListener`, which persists flush state for WAL-disabled v2 recovery. Tablet destruction currently removes the directory via `encryption_export::trash_dir_all`; the commented RocksDB destroy path notes a future replacement.

## Dependencies And Integration Points

The file integrates `engine_rocks` option/listener APIs, `engine_traits` tablet factory abstractions, `raftstore::RegionInfoAccessor`, `ForcePartitionRangeManager`, encrypted directory deletion, TiKV config resource builders, and `tikv_util::worker::Scheduler` for SST recovery. It depends on TiKV API version selection because CF options may differ between API modes.

## Risks

- `path.to_str().unwrap()` and `file_name().unwrap()` assume valid UTF-8 paths and valid tablet path shape.
- `destroy_tablet` ignores the result of `trash_dir_all`, so deletion failures can be hidden from callers.
- `set_state_storage` under `testexport` mutates through a raw pointer to shared `Arc` data and must remain test-only.
- Lite mode suppresses listeners/filters, so users must not expect compaction events, flow metrics, or SST recovery behavior in that mode.
- The range compaction filter on tablets is correctness-sensitive because it removes keys outside tablet range.

## Test Signals

`test_engine_factory` verifies tablet existence, duplicate open locking, destruction, and post-destroy absence. `test_engine_factory_compaction_filter` verifies the tablet range compaction filter removes keys outside `[start_key, end_key)` while retaining in-range keys after flush.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/engine_factory.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/errors.rs -->
# sources/storage-engines/tikv/src/server/errors.rs

## Purpose

This file defines the server-layer error envelope used by TiKV server components. It unifies IO, protobuf, gRPC, codec, raftstore, storage, engine, PD, HTTP, OpenSSL, worker scheduling, channel, and cluster-ID mismatch failures behind a single `Error` enum and `Result<T>` alias.

## Important APIs, Types, And Functions

- `Error` is a `thiserror::Error` enum with `#[from]` conversions for common subsystem errors.
- `Other(Box<dyn StdError + Sync + Send>)` carries arbitrary boxed errors.
- `SnapWorkerStopped(ScheduleError<SnapTask>)` represents snapshot-worker scheduling failure.
- `Sink`, `RecvError`, and `StreamDisconnect` model async/channel failures.
- `ClusterIDMisMatch { request_id, cluster_id }` reports request cluster ID mismatch explicitly.
- `pub type Result<T> = result::Result<T, Error>` is the local result contract.

## Control Flow

There is no runtime control flow beyond conversion and formatting. Call sites can use `?` to convert supported lower-level errors into `server::Error`, and error display/debug output is controlled by the enum variant annotations.

## State And Persistence Behavior

The file has no mutable state or persistence. It carries errors by value, including boxed dynamic errors for unsupported cases.

## Dependencies And Integration Points

It imports error types from `engine_traits`, `grpcio`, `hyper`, `openssl`, `pd_client`, `protobuf`, `raftstore`, `tikv_util`, `storage`, and the snapshot worker task type. It is a server boundary type rather than a storage-specific error type.

## Risks

- Several variants format with `{:?}` instead of user-facing display, which may produce verbose or unstable messages.
- `Other` erases structured error information.
- Adding new server tasks with schedule errors requires explicit variants if callers need automatic conversion.
- `ClusterIDMisMatch` is spelled with `MisMatch`, so renaming would be a compatibility churn point.

## Test Signals

No tests are defined in this file. Coverage is indirect through server paths that return `server::Result<T>` and use `?` on lower-level errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/errors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/gc_worker/compaction_filter.rs -->
# sources/storage-engines/tikv/src/server/gc_worker/compaction_filter.rs

## Purpose

This file implements the RocksDB write-CF compaction filter used to perform MVCC GC during compaction. It decides when a compaction should run GC based on MVCC table properties, removes stale write records, deletes corresponding default-CF long values, emits tasks for bottommost MVCC deletion marks, and records detailed metrics for filtered versions, failures, rollbacks, orphan versions, and deletion cleanup.

## Important APIs, Types, And Functions

- `GcContext` is a global context for constructing write compaction filters. It stores the disk DB, store ID, shared safe point, config tracker, feature gate, GC scheduler, and region info provider.
- `GC_CONTEXT: Mutex<Option<GcContext>>` is the global handoff from GC worker initialization into RocksDB compaction filter creation.
- `CompactionFilterInitializer<EK>` provides a default no-op implementation for unsupported engines and a RocksEngine implementation that installs `GcContext`.
- `WriteCompactionFilterFactory` implements `CompactionFilterFactory` and creates `WriteCompactionFilter` only when the safe point is initialized, the DB is not stalled, config and feature gates allow it, and table properties indicate enough garbage.
- `DeleteBatch<B>` wraps either an engine write batch or a vector of keys for multi-Rocks/tablet fallback, tracking smallest/largest affected keys for ingest latch protection.
- `WriteCompactionFilter` holds safe point, engine, pending default-CF deletes, scheduled MVCC deletion marks, current MVCC key prefix, per-key state, metrics, and optional test callbacks.
- `check_need_gc` evaluates input SST MVCC properties against safe point, ratio threshold, bottommost status, version counts, deletion counts, and maximum row versions.
- `is_compaction_filter_allowed` combines config and feature gate checks; the required feature version is 5.0.0 unless version checking is skipped.

## Control Flow

Filter factory creation locks `GC_CONTEXT`, reads the current safe point and config, rejects uninitialized or disallowed states, drops the lock, then checks input table properties. When a filter is created, RocksDB calls `featured_filter` for write-CF keys. `do_filter` splits the timestamp from the key, ignores versions newer than the safe point and non-value entries, switches per-user-key state when the MVCC key prefix changes, parses the write record, and removes rollback/lock records plus older records after the first retained Put/Delete before the safe point. For long Put values, `handle_filtered_write` schedules the default-CF payload delete. When a bottommost Delete write becomes the retained version and no older overlapping records remain, the filter queues the user key for `GcTask::GcKeys`.

Pending default-CF deletes are flushed in bounded batches with `WriteOptions::set_no_slowdown(true)` and an ingest latch over the affected key range. If inline flushing fails or the fallback vector path is used, the filter constructs `GcTask::OrphanVersions` so the GC worker can clean those default-CF versions later. On drop, the filter finalizes pending deletion marks, flushes pending writes, syncs WAL when it has a Rocks engine, and flushes local metrics.

## State And Persistence Behavior

The safe point is read from an `Arc<AtomicU64>` and is fixed per filter instance. Filter progress is in-memory and per-compaction. Persistence changes happen through delete write batches against default CF, scheduled GC tasks, and WAL sync after filter drop. `OrphanVersions` exists because a compaction result may be installed before default-CF cleanup finishes; the file explicitly notes a crash window where orphan versions can remain until a future default compaction filter exists.

## Dependencies And Integration Points

The file integrates RocksDB raw compaction filter APIs, MVCC table property decoding, TiKV transaction key and write parsing, the GC worker scheduler, region info lookup for later key cleanup, feature gating from PD, file-system IO type tagging, failpoints, and Prometheus metrics. It is initialized by `GcWorker::start_auto_gc` and consumed by RocksDB write-CF compactions.

## Risks

- `GC_CONTEXT` is global mutable process state; tests and multiple engine modes must clear or replace it carefully.
- Compaction filter correctness depends on write-CF ordering and timestamp parsing; malformed keys or values disable filtering after logging a failure.
- The orphan-version crash window can leave default-CF garbage.
- Inline delete flush uses no-slowdown and can fail under pressure, shifting load to async GC worker tasks.
- Bottommost deletion handling must not expose older versions; it only schedules deletion-mark cleanup when overlap tracking proves older records were removed.
- Ratio-threshold behavior can disable GC for negative or infinite values and force GC for values below 1.0.

## Test Signals

Tests cover feature-gate behavior, basic MVCC GC safety, deletion-mark handling across repeated compactions, MVCC property thresholds and bottommost behavior, `RemoveAndSkipUntil` safety across internal and bottommost levels, and `DeleteBatch` smallest/largest tracking. Failpoints cover write-batch flush failures, latch acquisition, filter entry, and test hooks for compaction execution.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/gc_worker/compaction_filter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/gc_worker/compaction_runner.rs -->
# sources/storage-engines/tikv/src/server/gc_worker/compaction_runner.rs

## Purpose

This file implements the automatic compaction runner. Unlike classic automatic GC, it does not directly scan and GC every region. Instead, it periodically evaluates regions using RocksDB table properties and optional MVCC read-activity signals, ranks compaction candidates, and manually compacts write/default CF ranges to let compaction filters reclaim space and improve read performance.

## Important APIs, Types, And Functions

- `CompactionCandidate` stores score, tombstone count, estimated discardable MVCC entries, total entries, row count, MVCC read versions scanned, and region metadata. Ordering is score-based for heap ranking.
- `CompactionRunnerHandle` owns the thread join handle and stop-signal sender.
- `CompactionRunner<S, R, E>` owns a safe point provider, region info provider, KV engine, stop receiver, stopped flag, and `GcWorkerConfigManager`.
- `start` spawns the runner on the `COMPACTION_RUNNER_THREAD` thread name and preserves thread-group properties.
- `run` polls config and safe point, collects candidates, compacts candidates, resets the MVCC read tracker, and sleeps until the next interval or stop signal.
- `collect_compaction_candidates` walks regions with `seek_region`, evaluates each one, and keeps a bounded top-N min heap based on check interval.
- `evaluate_range_candidate` reads write-CF table properties for a region, estimates tombstones and discardable versions, pulls MVCC read tracker data when enabled, and returns a scored candidate.
- `get_compact_score` applies tombstone or redundant-row thresholds and optionally adds weighted MVCC-read pressure.
- `compact_candidate` compacts write CF first, then default CF, with configurable bottommost-level force.

## Control Flow

The runner loop exits on stop. Each round clones a consistent config snapshot, reads the current GC safe point, skips work if the safe point is zero, then scans region metadata from the beginning of the keyspace. Candidate collection evaluates each region and retains only the best candidates to keep memory bounded. Candidate compaction rechecks each region with the current safe point before compaction, skips candidates no longer needing work, then invokes manual range compaction for write and default CF. The loop accounts for elapsed time and enforces a minimum 20-second inter-round gap when MVCC-read-aware scoring is enabled, giving the read tracker time to accumulate new observations after reset.

## State And Persistence Behavior

The runner holds no durable state. It mutates engine state indirectly via manual `compact_range_cf`, causing RocksDB to rewrite SST files and activate compaction filters. Metrics gauges and histograms record candidate counts, scores, tombstone/discardable distributions, MVCC read signals, and evaluation/compaction durations. Test/failpoint builds expose `FIRST_COMPACTION_CANDIDATE_REGION`.

## Dependencies And Integration Points

The runner depends on `GcSafePointProvider`, `RegionInfoProvider`, `KvEngine` table properties and manual compaction APIs, key encoding helpers, `GcWorkerConfigManager`, MVCC read tracker, Prometheus metrics, and failpoints. `GcWorker::start_auto_compaction` constructs it after initializing the global MVCC read tracker.

## Risks

- Region scanning uses synchronous `mpsc` callbacks around `seek_region`; provider stalls can block the runner.
- Score estimates are property-based and approximate timestamp distribution linearly between oldest/newest stale/delete timestamps.
- `num_entries - mvcc_properties.num_versions` assumes properties are internally consistent.
- `PartialOrd` over `f64` can encounter NaN; `Ord` maps unordered comparisons to `Equal`, which can affect heap ordering.
- If compactions are faster than expected, heap capacity derived from check-interval seconds may underutilize opportunities; if slower, the interval guard truncates processing.
- Manual compaction of both write and default CF can be IO-expensive and shares resources with foreground traffic.

## Test Signals

The file itself contains failpoints rather than normal tests. Failpoints mark thread start, runner start, candidate detection, candidate collection, specific table-property candidate shapes, and first-candidate selection. External tests can verify MVCC-aware prioritization through `FIRST_COMPACTION_CANDIDATE_REGION`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/gc_worker/compaction_runner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/gc_worker/config.rs -->
# sources/storage-engines/tikv/src/server/gc_worker/config.rs

## Purpose

This file defines runtime configuration for GC, compaction-filter GC, and automatic compaction. It also provides the online config manager that updates the version-tracked config and resizes the GC worker future pool when `num_threads` changes.

## Important APIs, Types, And Functions

- `AutoCompactionConfig` controls automatic compaction interval, tombstone thresholds, redundant-row thresholds, bottommost force, and MVCC-read-aware scoring.
- `AutoCompactionConfig::default` uses raftstore-like defaults: 5-minute checks, 10k tombstones, 30 percent tombstones, 50k redundant rows, 20 percent redundant rows, bottommost force off, MVCC read awareness off, scan threshold 1000, and read weight 3.0.
- `AutoCompactionConfig::validate` rejects zero intervals, percentage thresholds over 100, and negative MVCC read weight.
- `GcConfig` controls traditional GC ratio threshold, batch size, write bandwidth limit, compaction filter enablement and version-check override, worker thread count, and nested auto-compaction config.
- `GcConfig::validate` rejects zero batch size and zero thread count, then validates auto-compaction.
- `GcWorkerConfigManager` wraps `Arc<VersionTrack<GcConfig>>` and optional `FuturePool`.
- `ConfigManager::dispatch` applies online changes and scales the pool when `num_threads` is updated.

## Control Flow

Configuration is deserialized with kebab-case field names and defaults. Online config changes are cloned, inspected for `num_threads`, optionally applied to the worker future pool with `scale_pool_size`, then committed into `VersionTrack` through `OnlineConfig::update`. The manager logs both thread-count changes and the final change payload.

## State And Persistence Behavior

The file has no direct persistence. Runtime state lives in `VersionTrack<GcConfig>` so workers can track config versions without global locks. The optional pool reference lets config dispatch affect live concurrency. `ReadableDuration` and `ReadableSize` carry human-readable config units.

## Dependencies And Integration Points

It integrates `online_config`, `tikv_util::config::{ReadableDuration, ReadableSize, VersionTrack}`, and `yatp_pool::FuturePool`. `GcWorker`, `GcManager`, `CompactionRunner`, and `WriteCompactionFilterFactory` read this config through trackers and snapshots.

## Risks

- `ratio_threshold` is not validated here; downstream code treats negative or infinite values as disabling GC and values below 1.0 as always GC.
- MVCC read weight can be arbitrarily high, potentially over-prioritizing read-hot regions.
- Pool scaling is applied before the version-track update; if config update later failed, the pool would already be resized.
- `num_threads` field is logged as `gc.thread_count` in validation text, which may not exactly match the serialized field name.

## Test Signals

Direct tests are not in this file. `gc_worker.rs` contains `test_update_gc_thread_count`, which dispatches online `num_threads` changes and verifies the worker pool size changes from 1 to 5 and then to 2.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/gc_worker/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/gc_worker/gc_manager.rs -->
# sources/storage-engines/tikv/src/server/gc_worker/gc_manager.rs

## Purpose

This file implements the classic automatic GC manager. It polls PD for the GC safe point, tracks a shared safe-point atomic used by compaction filters, and when compaction-filter GC is not allowed, scans local leader regions and schedules `GcTask::Gc` work on the GC worker.

## Important APIs, Types, And Functions

- `AutoGcConfig<S, R>` contains safe point provider, region info provider, local store ID, polling interval, aggressive safe-point checking flag, and an optional post-round callback for tests.
- `GcManagerContext` owns stop-signal handling and exposes `sleep_or_stop` and `check_stopped`.
- `GcManagerState` maps internal state to metric tags (`initializing`, `idle`, `working`).
- `GcManagerHandle::stop` synchronously signals and joins the manager thread.
- `GcManager<S, R, E>` owns config, shared safe point, last safe-point check time, GC worker scheduler, stop context, config tracker, feature gate, and maximum concurrent tasks.
- `initialize` resets safe point to zero and tries to load an initial PD safe point without triggering immediate GC.
- `wait_for_next_safe_point` sleeps until the safe point advances.
- `try_update_safe_point` enforces monotonic safe points, updates the atomic, and emits safe-point metrics.
- `gc_a_round` scans regions, schedules bounded concurrent GC tasks, and rewinds when the safe point advances mid-round.
- `get_next_gc_context` uses `RegionInfoProvider::seek_region` and filters regions by local peer.

## Control Flow

`start` initializes state, installs a stop receiver, and spawns the manager thread. The main loop resets processed-region metrics, waits for a safe-point advance, and only runs range GC if `is_compaction_filter_allowed` is false. During a GC round it scans regions in key order, checks stop signals and compaction-filter eligibility, periodically refreshes the safe point, and schedules region GC tasks with callbacks that decrement a shared in-flight counter. If the safe point changes after progress has moved beyond the beginning, it finishes to the end, rewinds to the beginning, and continues until reaching the key where the new safe point was observed.

## State And Persistence Behavior

The manager persists no data itself. It stores the latest safe point in an `Arc<AtomicU64>` shared with compaction filter initialization. Region GC effects are delegated to `GcRunner` via scheduled tasks. Metrics track manager status and processed scanned/GCed regions. The concurrency controller is in-memory `Mutex<usize>` plus `Condvar`.

## Dependencies And Integration Points

The manager integrates `GcSafePointProvider` implementations such as PD clients, `RegionInfoProvider`, `Scheduler<GcTask<E>>`, feature gates, `GcWorkerConfigManager`, GC metrics, and `schedule_gc`. It is created by `GcWorker::start_auto_gc` after compaction-filter context initialization.

## Risks

- A lower safe point than the current one panics, assuming PD monotonicity.
- `max_concurrent_tasks - 1` can underflow if constructed with zero, though config validation and constructor callers are expected to prevent zero threads.
- If schedule fails because the worker is too busy, the callback path avoids decrementing in-flight count; this is intentional but easy to break when adding callback-bearing tasks.
- Region-provider callback or channel failure makes region scanning stop for that path.
- When compaction filter becomes allowed mid-round, `gc_a_round` exits early and relies on compaction-filter GC thereafter.

## Test Signals

Tests cover safe-point updates and waiting, initialization behavior, automatic GC without rewind, multiple rewind scenarios across bounded and unbounded region ranges, and worker-full scheduling via failpoint. Test utilities use mock safe-point and region providers plus a mock runner that records scheduled tasks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/gc_worker/gc_manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/gc_worker/gc_worker.rs -->
# sources/storage-engines/tikv/src/server/gc_worker/gc_worker.rs

## Purpose

This file implements the GC worker service and its task executor. It handles region GC, key-list GC from compaction filters, raw key GC, unsafe destroy range, orphan default-CF version cleanup, runtime config refresh, worker lifecycle, automatic GC startup, and automatic compaction startup.

## Important APIs, Types, And Functions

- `GcSafePointProvider` abstracts safe-point lookup; `Arc<PdClient>` implements it through `get_gc_safe_point`.
- `GcTask<E>` is the worker command enum: `Gc`, `GcKeys`, `RawGcKeys`, `UnsafeDestroyRange`, `OrphanVersions`, and test-only `Validate`.
- `GcRunnerCore<E>` owns store ID, engine, flow-info sender, write limiter, current config, config tracker, per-key-mode statistics, and coprocessor host.
- `GcRunner<E>` wraps `GcRunnerCore` and a YATP remote pool, spawning each scheduled task asynchronously after refreshing config.
- `get_regions_for_range_of_keys`, `get_keys_in_region`, and `init_snap_ctx` convert key batches into local regions and snapshot contexts.
- `GcRunnerCore::gc` runs range GC over a region after a table-property `need_gc` shortcut.
- `gc_keys` performs transactional MVCC GC for explicit keys, splitting work by region and flushing bounded `MvccTxn` batches.
- `raw_gc_keys` and `raw_gc_key` perform API v2 raw-key cleanup from explicit keys and safe point.
- `unsafe_destroy_range` bypasses Raft to delete a range directly, using fast file deletion plus key/blob cleanup for single RocksDB and per-region modifies for multi-RocksDB.
- `flush_deletes` handles vector fallback cleanup for orphan versions.
- `schedule_gc` and `sync_gc` are helper APIs for asynchronous and synchronous region GC.
- `GcWorker<E>` owns the lazy worker, scheduler, config manager, auto-GC handle, auto-compaction handle, feature gate, and region info provider.

## Control Flow

Scheduled tasks enter `GcRunner::run`, refresh config, clone runner core, and run on the future pool. `GcTask::Gc` checks MVCC properties before scanning region keys in `batch_keys` chunks and invokes `gc_keys`. `GcTask::GcKeys` and `RawGcKeys` operate on key vectors emitted by compaction filters, map them to local regions, and record handled versus wasted key metrics. `UnsafeDestroyRange` first emits flow notifications and coprocessor pre-delete hooks, then deletes files/ranges directly in local RocksDB or sends per-region delete-range modifies in multi-RocksDB mode. `OrphanVersions` acquires an ingest latch over the affected key span, then either writes the stored write batch synchronously or flushes individual deletes through the engine abstraction.

`GcWorker::start` starts the lazy worker with a `GcRunner`. `start_auto_gc` initializes the global compaction-filter context, creates `GcManager`, and starts its polling thread. `start_auto_compaction` initializes the MVCC read tracker and starts `CompactionRunner`. `Drop` stops manager, compaction runner, and worker only when the last cloned worker reference is released.

## State And Persistence Behavior

GC changes are persisted through `engine.modify_on_kv_engine`, raw/default-CF deletes, RocksDB range deletion APIs, and write batches. The write limiter is refreshed from online config and throttles GC write size. Statistics are accumulated per key mode and flushed to Prometheus counters after tasks. Unsafe destroy range also sends `FlowInfo` before/after events and hints range changes to the engine. The worker queue capacity is bounded by `GC_MAX_PENDING_TASKS`; unsafe destroy range uses `schedule_force` so it can still run when normal GC is full.

## Dependencies And Integration Points

This file integrates PD safe points, region metadata, raftstore coprocessor host, TiKV storage snapshots, MVCC reader/transaction GC logic, raw API v2 key/value encoding, RocksDB CF/range deletion APIs, flow-info signaling, failpoints, YATP pools, online config, compaction filter metrics, and auto-GC/auto-compaction components from sibling modules.

## Risks

- Unsafe destroy range bypasses Raft and relies on the caller guarantee that the range will not be accessed again.
- Region/key mapping assumes sorted key batches and local-peer filtering; gaps or stale region info can leave garbage.
- `keys.first().unwrap()` in key-GC paths requires non-empty key batches from callers.
- `OrphanVersions` for single RocksDB unwraps `kv_engine`; callers must only send write-batch orphan tasks where a local RocksDB exists.
- Multi-RocksDB unsafe destroy range has TODOs for flow info and region-size clearing parity.
- Config refresh happens per scheduled task, so long-running tasks keep the config snapshot they started with.

## Test Signals

Tests cover region selection for key GC, unsafe destroy range across boundary cases, compaction-filter key cleanup with region info, GC statistics, raw key GC, scan range limiting and large write-batch continuation, forced unsafe destroy range when the worker queue is full, key iteration across regions, multi-RocksDB GC/key/raw/destroy-range behavior, online thread-count scaling, and ingest-latch interaction for orphan-version cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/gc_worker/gc_worker.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/gc_worker/mod.rs -->
# sources/storage-engines/tikv/src/server/gc_worker/mod.rs

## Purpose

This module file defines the public surface of `server::gc_worker`, wires submodules together, re-exports worker/config/compaction APIs, and provides the shared table-property `check_need_gc` helper used by range GC.

## Important APIs, Types, And Functions

- Public modules: `compaction_filter` and `rawkv_compaction_filter`.
- Private modules: `compaction_runner`, `config`, `gc_manager`, and `gc_worker`.
- Re-exports include `WriteCompactionFilterFactory`, `CompactionCandidate`, `CompactionRunner`, `CompactionRunnerHandle`, `AutoCompactionConfig`, `GcConfig`, `GcWorkerConfigManager`, `AutoGcConfig`, `GcSafePointProvider`, `GcTask`, `GcWorker`, `STAT_RAW_KEYMODE`, `STAT_TXN_KEYMODE`, `sync_gc`, and `RawCompactionFilterFactory`.
- Test/failpoint exports include `TestGcRunner`, `gc_by_compact`, `FIRST_COMPACTION_CANDIDATE_REGION`, `MockSafePointProvider`, and `PrefixedEngine`.
- It re-exports `Callback`, `Error`, `ErrorInner`, and `Result` from storage pending a dedicated GC worker error type.
- `check_need_gc` is the module-level heuristic for deciding whether MVCC properties justify GC.

## Control Flow

The only functional control flow is `check_need_gc`: negative or infinite ratio threshold disables GC; threshold below 1.0 forces GC; if `props.min_ts` is above the safe point it skips; otherwise it triggers when versions exceed rows times threshold or versions exceed puts times threshold. It is deliberately an optimization and can be false positive because table properties are file-based.

## State And Persistence Behavior

The module file has no persistent state. It determines visibility and centralizes a stateless GC heuristic.

## Dependencies And Integration Points

It depends on `engine_traits::MvccProperties`, `txn_types::TimeStamp`, sibling modules, raw KV compaction filtering, and storage-level callback/error types. Its re-exports are the integration point used by the broader server and storage code to start GC workers, install compaction filters, schedule synchronous GC, and configure automatic compaction.

## Risks

- Re-exporting storage `Error` and `Result` couples GC worker API to storage errors; the TODO notes this should become a separate error type.
- `check_need_gc` is heuristic and can cause extra scans or skip work until later compaction/property changes.
- Public/private module boundaries are important: `compaction_runner` is private but selected types are public, so new APIs must be intentionally re-exported.

## Test Signals

Tests validate `check_need_gc` edge cases for disabled/forced thresholds and real RocksDB MVCC properties. The property test verifies transitions from no-GC, to GC after deleted multi-version keys, to no-GC after manual cleanup, and GC for a single lock version.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/gc_worker/mod.rs -->
