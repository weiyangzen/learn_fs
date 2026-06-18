# subset-b-008926 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/read_pool.rs -->
# sources/storage-engines/tikv/src/read_pool.rs

## Purpose

`read_pool.rs` builds and manages TiKV's read execution pools. It supports the older three-pool `FuturePools` mode split by request priority and the newer unified YATP pool (`ReadPool::Yatp`) that combines priority scheduling, resource-control admission, task eviction, metrics, thread-local engine setup, and online resizing.

The file is on the hot read path. Callers use `ReadPool::handle()` to get a cheap `ReadPoolHandle`, then enqueue read futures through `spawn` or `spawn_handle`. The unified mode is also used by server busy checks because it tracks task queue depth and an EWMA of task poll duration to estimate wait time.

## Important APIs, types, and functions

`ReadPool` owns the actual pools. `FuturePools` contains high, normal, and low `FuturePool`s. `Yatp` owns a `yatp::ThreadPool<TaskCell>`, per-resource-priority running-task gauges, a thread-count gauge, max-task accounting, optional `ResourceController` and `ResourceGroupManager`, and a shared `TimeSliceInspector`.

`ReadPoolHandle` is the cloneable execution interface. `spawn` selects a `FuturePool` by `CommandPri` or constructs a YATP `TaskCell` with multilevel scheduling metadata. `spawn_handle` wraps `spawn` with a oneshot channel so callers can await a task result. `scale_pool_size`, `set_max_tasks_per_worker`, `get_queue_size_per_worker`, and `check_busy_threshold` are used by config management and request admission.

`admission_and_enqueue` is the key unified-pool enqueue path. It asks the resource group manager for an admission decision before any capacity or eviction logic. Rejected tasks return `ReadPoolError::Rejected`; delayed tasks sleep outside the pool, with a warning for delayed high-priority reads. After admission, it checks `running_tasks` against `max_tasks`; if resource control is enabled it tries `remote.try_evict_lowest(estimated_priority)` and decrements the evicted task's priority gauge, otherwise it returns `UnifiedReadPoolFull`.

`TimeSliceInspector` samples YATP `TASK_POLL_DURATION` histograms across scheduling levels and maintains an atomic EWMA in nanoseconds. `get_estimated_wait_duration` multiplies EWMA by queue size per worker, and `check_busy_threshold` converts excessive wait estimates into `errorpb::ServerIsBusy`.

`build_yatp_read_pool` and `build_yatp_read_pool_with_name` configure the unified pool. They set thread counts from `UnifiedReadPoolConfig`, install TLS storage engine state in `after_start`, set foreground-read IO type, destroy TLS engine state in `before_stop`, select priority-pool vs multilevel-pool depending on resource control, register metrics, and preserve optional task wait metrics.

`ReadPoolCpuTimeTracker`, `ReadPoolConfigRunner`, and `ReadPoolConfigManager` implement online pool resizing. The runner receives config tasks for max thread count, auto-adjust, max tasks per worker, and CPU threshold, and also wakes every `READ_POOL_THREAD_CHECK_DURATION` to auto-adjust thread count.

`ReadPoolError` distinguishes old `FuturePoolFull`, unified full, resource-control rejection, and oneshot cancellation.

## Control flow

In legacy mode, `spawn` maps `CommandPri::{High,Normal,Low}` directly to one of three `FuturePool`s and returns a ready future containing the spawn result.

In unified mode, `spawn` derives `TaskPriority` from `TaskMetadata::override_priority`, maps background resource-limited jobs to low scheduling level, maps high/low `CommandPri` to fixed YATP levels, and leaves normal foreground work for multilevel scheduling. It stores metadata in `Extras`, wraps the future in `ControlledFuture` and `with_resource_limiter` when resource control is enabled, and ensures the running-task gauge is decremented when the future completes. The async `admission_and_enqueue` then admits, optionally delays, evicts if allowed, increments the gauge, and calls `remote.spawn`.

The resize path is driven by `ReadPoolConfigManager::dispatch` and timer callbacks. Direct config changes schedule a `Task`; `ReadPoolConfigRunner::run` applies the new core size, auto-adjust flag, max-tasks-per-worker, or CPU threshold. Timer callbacks call `adjust_pool_size`, which measures read-pool CPU usage from Linux thread stats, YATP task-handling time from metrics, current queued/running tasks, and process CPU. It scales in when CPU-threshold pressure is high, scales back out toward the configured core count when read-pool CPU is below threshold, and otherwise applies thread-utilization scale-in/out rules bounded by min/core/max counts.

## State and persistence behavior

This file does not persist user data. Its state is in-memory pool state: running-task gauges, thread counts, max-task limits, EWMA samples, previous CPU/time counters, and scheduled config tasks. Persistent effects are indirect: read futures execute storage work using TLS engine handles installed on read-pool worker threads, and resource-control debt/accounting can be updated by `ControlledFuture` and `with_resource_limiter`.

Metrics are Prometheus state: `tikv_unified_read_pool_running_tasks`, `tikv_unified_read_pool_thread_count`, and `tikv_unified_read_pool_evicted_tasks`. The task-poll histogram is supplied by YATP.

## Dependencies and integration points

The pool integrates with `yatp`, `tikv_util::yatp_pool`, `resource_control`, `kvproto::kvrpcpb::CommandPri`, `tikv_util::resource_control::TaskMetadata`, `file_system::set_io_type`, storage engine TLS helpers, `FlowStatsReporter` metric flushing, online config through `ConfigManager`, and `tikv_util::worker::{Worker,Scheduler}`.

Server-level callers depend on `check_busy_threshold` to reject requests when estimated queueing delay is too high. The config subsystem depends on `ReadPoolConfigManager` to apply online changes under the `"unified"` config module.

## Risks and edge cases

Admission is intentionally before eviction; changing that order can let a delayed or rejected task evict already queued work. Running-task gauges must stay balanced across normal completion and eviction; leaked increments would make the pool permanently look full. `get_queue_size_per_worker` divides by pool size, so the unified pool must never be scaled to zero. CPU-based resizing depends on thread-name matching and Linux thread stats, so renamed worker threads or platform gaps can disable accurate CPU control. The YATP task-poll EWMA is a coarse cross-level average; it can over- or under-estimate specific priority classes.

`scale_pool_size` recalculates `max_tasks` using the previous per-worker capacity. A bad current `pool_size` or unexpected zero value would distort capacity. `ProcessStat::cur_proc_stat().unwrap()` in config manager construction assumes process-stat availability.

## Test signals

Tests cover unified-pool full behavior, manual scale up/down, high-priority eviction, EWMA calculation, CPU-threshold config shape, CPU-threshold scale-in/out behavior, task-poll metrics, and reset notification when auto-adjust is disabled. The eviction test explicitly verifies resource-group priority based eviction when the pool is full. These tests are focused on in-process behavior and metrics; they do not prove production thread-stat accuracy across platforms.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/read_pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/config.rs -->
# sources/storage-engines/tikv/src/server/config.rs

## Purpose

`server/config.rs` defines TiKV server-layer configuration, default values, validation, and online update handling. It covers network endpoints, gRPC concurrency and memory, raft client queues, snapshot concurrency and IO limits, coprocessor endpoint limits, status server options, request batching, memory-based message rejection, health feedback, slow-store network inspection, graceful shutdown, and store labels.

The file is the main boundary between static TOML configuration, online config updates, gRPC resource quota resizing, snapshot worker refresh, and coprocessor config dispatch.

## Important APIs, types, and functions

`GrpcCompressionType` is a serde-friendly mirror of grpc-rs compression algorithms. `Config` derives `OnlineConfig` and uses `serde(rename_all = "kebab-case")`. Many identity, listener, concurrency, and deprecated endpoint fields are marked `#[online_config(skip)]`, while selected runtime tunables such as `max_grpc_send_msg_len`, snapshot limits, `grpc_memory_pool_quota`, endpoint memory quota, `snap_io_max_bytes_per_sec`, `snap_max_total_size`, graceful shutdown timeout, and hidden/simplified metrics fields remain online configurable.

`Config::default` computes CPU-aware defaults. `DEFAULT_GRPC_RAFT_CONN_NUM` is `floor(cpu_quota / 8)` clamped to 1..4, and `DEFAULT_GRPC_CONCURRENCY` is three times that value plus two. Endpoint memory quota defaults to 12.5 percent of available memory but at least 500 MB. Endpoint max concurrency is at least four.

`Config::validate` normalizes advertise addresses, rejects invalid listener combinations, enforces nonzero snapshot and gRPC memory values, checks endpoint recursion and max-handle duration, validates gRPC send/window sizes, validates labels, checks forward connection count and memory reject ratio, migrates too-large legacy `heavy_load_threshold` to 75, checks network inspection interval lower bound, warns on disabled graceful shutdown timeout, and enforces raft connection/queue size consistency.

`grpc_compression_algorithm`, `end_point_request_max_handle_duration`, and `optimize_for` are helper APIs used by server construction and region-size based tuning.

`ServerConfigManager` implements `ConfigManager`. It applies online changes to an `Arc<VersionTrack<Config>>`, resizes the gRPC `ResourceQuota` when `grpc_memory_pool_quota` changes, schedules `SnapTask::RefreshConfigEvent`, and forwards the change to the coprocessor config manager.

`validate_label_key` and `validate_label_value` enforce Kubernetes-style-ish label syntax using regexes. Keys may optionally start with `$` but otherwise must begin and end with alphanumeric characters; values may be empty and allow `-A-Za-z0-9_./`.

## Control flow

Startup constructs `Config::default`, deserializes user config over it, then calls `validate`. Validation may mutate defaults: empty `advertise_addr` falls back to `addr`, non-unspecified status address may become `advertise_status_addr`, and legacy heavy-load thresholds above 100 are reset to 75.

Online updates enter `ServerConfigManager::dispatch`. The manager clones the incoming `ConfigChange`, applies it through `VersionTrack::update`, separately resizes the grpc-rs quota if the memory quota field changed, schedules snapshot config refresh best-effort, dispatches to the coprocessor manager best-effort, logs errors for side-effect failures, and returns success unless the version-track update itself fails.

`optimize_for` adjusts `end_point_request_max_handle_duration` only if it is unset. Regions below 256 MB use the 60 second default; larger regions scale by region-size multiples capped at 1800 seconds.

## State and persistence behavior

The configuration itself is in-memory once loaded, but it originates from persisted config files or online config sources outside this file. `VersionTrack<Config>` stores live server config snapshots. `ResourceQuota::resize_memory` mutates grpc-rs runtime quota in place. Snapshot and coprocessor changes are propagated through schedulers/managers; this file does not write RocksDB or raft state.

Validation mutates `Config` values before use, so callers should treat `validate` as both checking and normalizing.

## Dependencies and integration points

This module depends on `tikv_util::config` helpers, `SysQuota`, grpc-rs `CompressionAlgorithms` and `ResourceQuota`, `online_config`, raftstore store config exports, storage config exports, snapshot tasks, coprocessor config manager, and `engine_traits::PerfLevel` serde helpers. It is consumed by the server bootstrap path, online config controller, snapshot subsystem, gRPC server setup, coprocessor endpoint setup, raft client setup, and status server setup.

## Risks and edge cases

Address normalization has important semantics: unspecified `0.0.0.0` can be a valid bind address but invalid advertise address, so fallback is conditional. `advertise_status_addr` must not equal `advertise_addr`. `grpc_memory_pool_quota` is cast to `usize` during validation and resize; extremely large values need platform awareness. `reject_messages_on_memory_ratio` rejects negative values but permits values above 1.0, which may be intentional but weakly bounded. Online dispatch logs snapshot/coprocessor dispatch failures but still returns `Ok`, so operators may see partial application.

Deprecated endpoint fields remain in the struct for compatibility and are hidden/skipped for online config. Label regexes are stricter for keys than values, which tests document.

## Test signals

`test_config_validate` covers advertise fallback, default CPU-derived gRPC values, nonzero limits, recursion limit, memory quota, max-handle duration, invalid bind/advertise cases, duplicate advertise addresses, gRPC message/window limits, and label value validation. `test_store_labels` exercises key/value regex edge cases including empty strings, prefixes/suffixes, `$`, path separators, and non-ASCII input.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/debug.rs -->
# sources/storage-engines/tikv/src/server/debug.rs

## Purpose

`server/debug.rs` implements the classic raftstore debugger over shared RocksDB KV and raft engines. It exposes inspection, compaction, region metadata repair, MVCC repair, config modification, flashback, reset-to-version, and a small HTTP debug toggle for duplicate-key diagnostics. The code is operationally sensitive because several APIs intentionally rewrite raft metadata, raft logs, and MVCC column families.

The `Debugger` trait defined here is also implemented by `debug2.rs`, making this file the compatibility contract for debug tooling across raftstore generations.

## Important APIs, types, and functions

`Error` distinguishes invalid arguments, not-found states, boxed operational errors, engine-trait errors, and flashback failures. `RegionInfo` groups `RaftLocalState`, `RaftApplyState`, and `RegionLocalState`.

`BottommostLevelCompaction` converts HTTP/protobuf/debug options into RocksDB `DBBottommostLevelCompaction`.

`Debugger` declares the debug surface: raw gets, raft-log reads, region info and size, MVCC scanning, manual compaction, all-region listing, store identity, RocksDB stats, online config mutation, region property extraction, reset/flashback, statistics attachment, and range properties.

`DebuggerImpl<ER,E,L,K>` owns `Engines<RocksEngine, ER>`, optional Rocks statistics, `ResetToVersionManager`, `ConfigController`, and optional `Storage` for flashback. `InnerRocksEngineExtractor` permits raft DB access only when the raft engine is also a `RocksEngine`; generic raft engines reject direct raft DB reads.

Repair helpers include `set_region_tombstone`, `set_region_tombstone_by_id`, `recover_regions`, `recover_all`, `bad_regions`, `remove_failed_stores`, `drop_unapplied_raftlog`, and `recreate_region`. MVCC repair is implemented by `recover_mvcc_for_range` and `MvccChecker`.

`dump_default_cf_properties` and `dump_write_cf_properties` decode RocksDB range properties and MVCC user properties. `handle_dup_key_debug`, `handle_check`, and `handle_enable_debug` implement `/debug/dup-key/*` HTTP endpoints around `txn_types::ENABLE_DUP_KEY_DEBUG`.

## Control flow

Simple read APIs validate DB/CF combinations, select an engine, and read raw values or protobuf messages. `region_info` independently reads raft local state from the raft engine and apply/region state from KV CF_RAFT, returning not found only when all three are absent. `region_size` scans encoded region bounds in each requested CF and sums key/value bytes.

Manual compaction validates the DB/CF pair, resolves a column-family handle, builds `CompactOptions` with max subcompactions and bottommost-level choice, then calls RocksDB `compact_range_cf_opt`.

Tombstone-by-PD-region validates that local region state exists, the local peer belongs to this store, the target region has a higher conf version, and the target peers no longer include the same local peer. Only if all requested tombstones pass does the batched write sync to KV. Tombstone-by-id is more direct: it loads each local region state and marks it tombstone if present.

`remove_failed_stores` prevents removing the local store itself, scans selected or all region states, removes peers belonging to failed stores, optionally promotes a single remaining learner if no voters remain, preserves region epoch, and sync-writes updated region states.

`drop_unapplied_raftlog` loads region/apply/raft state, skips tombstones and already-applied regions, sets raft `last_index` and apply `commit_index` to `applied_index`, writes apply state to KV CF_RAFT, writes raft state through a raft log batch, garbage-collects raft entries `(applied_index + 1)..(last_index + 1)`, consumes the raft batch synchronously, and calls `kv.sync`.

`recreate_region` rejects invalid ranges and overlap with existing non-tombstone regions, then creates missing `RegionLocalState`, initial `RaftApplyState`, and initial `RaftLocalState` in synced KV and raft batches.

`MvccChecker` walks lock, default, and write CF iterators in key order. For each user key it deletes orphan or stale locks, orphan default records, and write records that require but lack a matching default record. `recover_mvcc_for_range` loops in write-batch chunks of 10240 fixes and can run read-only. `recover_all` divides the full data keyspace by approximate split keys and processes ranges on named threads.

Flashback first checks region flashback state against prepare/finish mode, builds a KV RPC context from region epoch and local peer, converts encoded keys back to raw keys, then calls prepare or finish flashback futures and maps response/region errors into `FlashbackFailed`.

## State and persistence behavior

This file directly reads and writes persistent TiKV state. KV CF_RAFT stores region local state and apply state; the raft engine stores raft local state and raft log entries; data CFs store MVCC lock/default/write records. Repair paths use synchronous write options or synchronous raft batch consumption for durability. `remove_failed_stores`, tombstoning, raft-log dropping, and region recreation are metadata mutations that can change restart behavior.

`reset_to_version` delegates persistent data rollback orchestration to `ResetToVersionManager`. Flashback executes through the storage layer and therefore participates in normal region/epoch checks. The duplicate-key debug flag is only an in-memory atomic.

## Dependencies and integration points

The debugger integrates with `engine_rocks`, `engine_traits`, `kvproto::debugpb/kvrpcpb/raft_serverpb`, `raftstore::store::PeerStorage`, raft `RawNode`, `ConfigController`, storage `Storage`, lock manager traits, `txn_types`, RocksDB range properties, hyper HTTP, and TiKV worker/thread utilities. It is used by debug services and administrative tooling, and it provides the trait that `debug2.rs` reuses for raftstore-v2.

## Risks and edge cases

The destructive helpers require strong operator correctness. Tombstoning by id bypasses the PD-region conf-version and scheduled-peer checks used by `set_region_tombstone`. `remove_failed_stores` intentionally leaves region epoch unchanged to avoid another class of inconsistency, but that also means metadata is manually divergent from PD until repaired. `drop_unapplied_raftlog` discards unapplied raft entries and must only be used when losing them is acceptable. `recreate_region` only checks local overlap and existing local metadata.

Several paths use `unwrap` after earlier assumptions (`region_local_state.unwrap`, storage existence for flashback, worker construction, iterator operations). `MvccChecker` has `unimplemented!` for shared locks returned by `txn_types::parse_lock`, so shared-lock data would panic. `divide_db(parts)` subtracts one from `parts`, so callers must avoid zero. Flashback unwraps store identity, region info, storage, and peer lookup before returning the async future.

## Test signals

Tests cover region overlap, DB/CF validation, raw get, raft log fetch, region info, region size, MVCC scan invalid inputs, tombstoning by PD region and by id, failed-store removal and learner promotion, dropping unapplied raft logs, bad-region detection through RawNode reconstruction, region recreation overlap checks, MVCC checker fix cases, raw scan boundaries, store identity, and manual compaction. The tests use temporary Rocks engines and mock storage/lock-manager types, so they are strong unit signals for local behavior but not full-cluster safety proofs.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/debug.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/debug2.rs -->
# sources/storage-engines/tikv/src/server/debug2.rs

## Purpose

`server/debug2.rs` implements the same `Debugger` trait for raftstore-v2, where raft metadata lives in a raft engine and key/value data is split into per-region tablets managed by `TabletRegistry<RocksEngine>`. It adapts classic debug operations to tablet lookup, persisted apply-index semantics, and region-range fanout.

The file shares repair primitives from `debug.rs` where possible, especially MVCC recovery and property dumping, but rewrites routing and persistence around tablet caches and raft-engine log batches.

## Important APIs, types, and functions

`DebuggerImplV2<ER>` owns a `TabletRegistry<RocksEngine>`, raft engine, optional KV/raft statistics, and `ConfigController`. Its public helpers mirror classic debugger operations: `recover_regions`, `recover_all`, `bad_regions`, `set_region_tombstone`, `set_region_tombstone_by_id`, and `drop_unapplied_raftlog`.

`MvccInfoIteratorV2` scans MVCC info across tablet boundaries. It keeps sorted active region states, the current region, requested encoded start/end bounds, a limit, and an optional `MvccInfoScanner`. `seek_region`, `smaller_key`, and `larger_key` help find the region and clipped scan range for each tablet.

`range_in_region`, `find_region_states_by_key_range`, `find_region_state_by_key`, `get_tablet_cache`, `get_all_active_region_states`, and `deivde_regions_for_concurrency` are the routing helpers that map global encoded ranges or raw keys to region/tablet work.

`new_debugger` under test/testexport builds a raftstore-v2 debugger from a TiKV config, tablet registry, and raft log engine.

## Control flow

Point reads call `find_region_state_by_key` on the key without the data prefix, load or reuse the tablet for that region, and read the requested CF from that tablet. `scan_mvcc` validates bounds, collects all non-tombstone region states, sorts them by region start key, and constructs `MvccInfoIteratorV2`; the iterator scans the current tablet until exhausted, advances to the next region by current end key, clips the requested range to the next region, and stops on limit or no further region.

`region_info` differs from classic debug: it first reads the flushed index for CF_RAFT and uses that persisted applied index to fetch apply and region state. It then overwrites `apply_state.applied_index` with the persisted applied value because that is the restart-visible state. This intentionally ignores newer apply-state records that are not visible at the persisted flushed index.

`region_size`, `get_region_properties`, and `get_range_properties` load tablets and scan only the region-overlapped encoded bounds. `compact` rejects raft DB compaction, finds all normal regions overlapping the requested encoded range, then runs RocksDB manual compaction on each tablet with clipped start/end keys.

`recover_regions` skips non-normal regions, loads each region tablet, and calls `recover_mvcc_for_range` over the region's raw start/end keys. `recover_all` groups active regions by approximate tablet size, opens all tablets for a group, and runs recovery concurrently with one thread per group.

`bad_regions` iterates raft groups, loads persisted region state, skips tombstone/applying, verifies a local peer exists, constructs raftstore-v2 `Storage`, and validates it through `RawNode::new`.

Tombstoning validates the same PD-region conditions as classic debug but writes through raft-engine log batches using the region's apply index. Tombstone-by-id also requires an apply state so it can write region state at the applied index. `drop_unapplied_raftlog` mirrors the classic algorithm but writes apply/raft state and GC records entirely through the raft engine.

## State and persistence behavior

Persistent state is split between the raft engine and per-region Rocks tablets. Region/apply/raft state and store identity are read/written via raft-engine APIs and log batches. KV data and MVCC records are read or repaired in tablets. Tablet loading uses `TabletContext` from region state and tablet index; a missing tablet can be loaded from the registry, and failures are surfaced as boxed errors.

The file does not implement `reset_to_version` or key-range flashback for raftstore-v2; both are `unimplemented!`, so calling them will panic. Config mutation still delegates to `ConfigController`. Statistics are appended from opened tablets plus optional `RocksStatistics`.

## Dependencies and integration points

This module depends on `engine_traits::{RaftEngine, TabletRegistry, CachedTablet, TabletContext}`, `raftstore_v2::Storage`, raftstore coprocessor helpers for approximate middle/size, `keys` data-prefix helpers, `debug.rs` trait/types/helpers, RocksDB compaction utilities, `ConfigController`, and MVCC scanner/collector types. It is selected for raftstore-v2 debug services and preserves the external `Debugger` trait expected by callers.

## Risks and edge cases

Several helpers unwrap raft-engine iteration results, region states, tablet latest handles, and scanner construction. `find_region_state_by_key` linearly scans raft groups and breaks if the matching region is not normal, returning not found. `get` slices `key[DATA_PREFIX_KEY.len()..]`, so callers must pass encoded data keys with the expected prefix. `MvccInfoIteratorV2` contains duplicated assertions that check `iter_start` twice and do not check `iter_end`; empty clipped ranges may panic or behave unexpectedly. The misspelled `deivde_regions_for_concurrency` is harmless but visible.

`range_in_region` accepts empty ranges and sentinel bounds as full-range requests; incorrect prefix handling would route compaction/properties to wrong tablet subranges. Raft DB compaction is explicitly disallowed in v2 even though `validate_db_and_cf` accepts `(Raft, default)` before `compact` rejects it. `recover_all` groups by approximate size, so skewed estimates can still produce uneven work.

## Test signals

Tests cover point get routing and tombstone rejection, raft log fetch, persisted-index-aware region info, region size with untrimmed tablet data, raft compaction rejection, range/region overlap clipping for first/last/full regions, even and uneven region grouping by approximate size, bad-region detection, PD-style tombstoning, tombstone-by-id, dropping unapplied raft logs including invisible newer apply-state records, and active-region listing that filters tombstones. These tests directly target raftstore-v2 routing and persistence semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/debug2.rs -->
