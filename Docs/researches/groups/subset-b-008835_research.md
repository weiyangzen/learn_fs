# subset-b-008835 research

Grouped research for TiKV in-memory region cache engine sources under `sources/storage-engines/tikv/components/in_memory_engine/src`. Each section is source-tree-aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/background.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/src/background.rs

## Purpose

Implements all asynchronous maintenance for the in-memory engine: loading cache regions from RocksDB snapshots, periodic GC/filtering, memory-pressure eviction, top-region load/evict decisions, delayed range deletion, lock-CF tombstone cleanup, optional cross-check startup, pending-region load triggering through raftstore, and PD region-label cache hints.

## Important APIs, Types, And Functions

`BackgroundTask` is the central worker command enum. Its variants cover `Gc(GcTask)`, `LoadRegion`, `MemoryCheckAndEvict`, `DeleteRegions`, `TopRegionsLoadEvict`, `CleanLockTombstone`, `TurnOnCrossCheck`, `SetRocksEngine`, and `CheckLoadPendingRegions`. `BgWorkManager` owns the primary worker, delete worker scheduler, ticker worker, engine core, and optional `RegionInfoProvider`; its `schedule_task` routes delete work to a separate scheduler and everything else to the main background runner. `PdRangeHintService` implements `RangeHintService` and watches PD region-label rules with label key `cache`, loading or evicting ranges when rules are added or removed.

`BackgroundRunner` is the main `Runnable`/`RunnableWithTimer`. It fans work out to dedicated workers/remotes: sequential region load, delete range, sequential GC, load/evict, lock cleanup, and optional cross-check worker. `BackgroundRunnerCore` contains shared engine/memory/statistics state and implements `regions_for_gc`, `gc_region`, snapshot-load completion/failure handling, and `top_regions_load_evict`. `DeleteRangeRunner` processes `DeleteRegions` and delays deletion while regions are being written or GCed. `Filter` is the GC compaction-filter analog for write/default CFs, with `split_ts` and `parse_write` validating MVCC key/value formats.

## Control Flow

`BgWorkManager::new` starts `BackgroundRunner` and `start_tick`. The ticker fires GC at `gc_run_interval`, load/evict at `load_evict_interval`, and pending-region checks about every five seconds. GC obtains a PD TSO, computes a safe point as current physical time minus the configured interval, schedules `BackgroundTask::Gc`, and the runner then asks RocksDB for the oldest live snapshot sequence number before spawning per-region filtering. The safe point used for each region is additionally capped by active in-memory snapshots and historical evicted-region snapshots.

Region loading is scheduled from `RegionCacheMemoryEngineCore::prepare_for_apply` after a pending region is marked `Loading` and a RocksDB snapshot is captured. `do_load_region` rejects canceled or stop-threshold loads, scans all `DATA_CFS` over the region range, inserts visible snapshot keys into skiplist CFs with the snapshot sequence number, accounts memory per entry, and aborts if capacity is reached. After loading, it fetches PD TSO and immediately runs `Filter` over the loaded region to remove old MVCC versions before marking the region `Active`; failures and cancellations mark regions evicting and enqueue delete-range work.

Memory pressure enters through `MemoryCheckAndEvict`, which delegates to `RegionStatsManager::evict_on_evict_threshold_reached` and clears the `memory_checking` flag when finished. Periodic `TopRegionsLoadEvict` collects hot regions and stale cached regions from `RegionStatsManager`, evicts selected cached regions, waits for eviction callbacks, then loads only as many new pending regions as the stop-load threshold can likely fit. `CheckLoadPendingRegions` sends raft casual messages to region leaders so a callback can call `prepare_for_apply` with a fresh disk snapshot.

## State And Persistence Behavior

The module does not create durable IME state. It mirrors RocksDB snapshot data into process-local skiplists and persists only indirectly by reading RocksDB snapshots and PD metadata. Region states and safe points live in `RegionManager`; `Loading`, `LoadingCanceled`, `Active`, `Evicting`, and historical snapshot metadata gate load completion, GC, and deletion. Memory is controlled through `MemoryController::acquire`/`release`; if an inserted `InternalBytes` later drops, it releases its recorded allocation. Metrics record memory usage, cache counts, safe points, GC filtering totals, and load/GC durations.

Deletes are deliberately asynchronous. `DeleteRangeRunner` removes all CF data for evicting regions only when region metadata shows no active write or GC. It then calls `RegionManager::on_delete_regions`, which is the point where region metadata and eviction callbacks can be finalized. GC deletion order is conservative: `Filter` caches MVCC delete keys and skiplist tombstones so older versions are removed before the delete marker that hides them.

## Dependencies And Integration Points

Depends on `engine_rocks` for `RocksEngine`/`RocksSnapshot`, `engine_traits` for CF names, region cache traits, snapshots, iterators, range hints, and eviction callbacks, `pd_client` for TSO and GC-safe-point access, `raftstore` for region info and casual load callbacks, `tikv_util::worker` for scheduling, `crossbeam` epoch/skiplist iteration safety, `txn_types` for MVCC keys and writes, and local modules `region_manager`, `region_stats`, `region_label`, `memory_controller`, `keys`, `write_batch`, `metrics`, and `cross_check`. Public integration is through `BgWorkManager`, `BackgroundRunner`, `BackgroundTask`, `GcTask`, and `PdRangeHintService`, mostly re-exported or called by `engine.rs`.

## Risks

The code is concurrency-sensitive: deletion must not race apply writes or GC, loading can be canceled while region epochs split, and GC must respect active snapshots plus historical evicted snapshots. Safe-point computation depends on PD TSO availability and wall-clock/physical timestamp assumptions. Memory accounting is approximate because skiplist node overhead is estimated, so thresholds can be crossed during load. Filter correctness is high-risk because deleting the wrong MVCC write/default pair can expose stale versions or remove visible values. `start_tick` updates `tso_timeout` from the old GC interval before assigning the new interval, which is worth reviewing if interval changes are important. PD label-watch handling currently has a TODO for richer eviction semantics when cache labels change.

## Test Signals

The in-file tests cover filter behavior, delete writes, region-scoped GC, GC after split, overwrite writes, snapshot-blocked GC, historical-region snapshot constraints, background load from RocksDB, GC-region selection, PD label hint loading and removal, load stop threshold, load capacity failure cleanup, online memory config changes, and PD TSO use for GC. Failpoints under `tests/failpoints/test_memory_engine.rs` exercise cancellation, write-batch interactions, and background timing. Metrics and logs are also key operational signals for memory pressure, safe-point drift, and load/evict decisions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/background.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/config.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/src/config.rs

## Purpose

Defines the online configuration contract for the in-memory engine and validates derived memory thresholds, timing intervals, and default capacity sizing against block-cache and region-size inputs.

## Important APIs, Types, And Functions

`InMemoryEngineConfig` is a `Serialize`, `Deserialize`, `OnlineConfig` struct using kebab-case field names. Its fields include `enable`, optional `capacity`, optional `evict_threshold`, optional `stop_load_threshold`, `gc_run_interval`, `load_evict_interval`, `mvcc_amplification_threshold`, skipped `cross_check_interval`, and hidden skipped `expected_region_size`. `Default` disables IME with a three-minute GC interval, five-minute load/evict interval, MVCC amplification threshold 10, and no capacity thresholds. `validate` mutates the config in place, computing defaults and rejecting invalid combinations. Accessors `capacity`, `evict_threshold`, and `stop_load_threshold` return `usize` values with zero for unset fields. `config_for_test` provides a fully enabled small test profile. `InMemoryEngineConfigManager` wraps `Arc<VersionTrack<InMemoryEngineConfig>>` and applies `ConfigChange` through online config updates.

## Control Flow

Validation returns immediately when `enable` is false. For enabled configs without manual capacity, it derives capacity as twice 10% of block-cache capacity, disables IME if that value is too small or not larger than region split size, clamps it to 5 GiB, stores it, and subtracts half from block-cache capacity. It then derives `evict_threshold` as capacity minus the smaller of 10% capacity or ten seconds of estimated write throughput, unless supplied; supplied values must be below capacity. It derives `stop_load_threshold` below the eviction threshold, bounded by either 15% of capacity or two region sizes plus reserved write throughput, unless supplied; supplied values must not exceed eviction threshold. It finally enforces GC interval in `[10s, 600s]` and load/evict interval at least 120s.

## State And Persistence Behavior

Config is process state tracked through `VersionTrack`, with changes applied online by `InMemoryEngineConfigManager::dispatch`. It does not persist data directly, but its values control when background workers load, evict, GC, and stop admitting new regions. The validation step can mutate external block-cache capacity, so startup configuration has cross-component memory side effects.

## Dependencies And Integration Points

Uses `online_config` for dynamic updates, `tikv_util::config::{ReadableDuration, ReadableSize, VersionTrack}`, raftstore split-size defaults, and serde. `RegionCacheMemoryEngine::with_region_info_provider`, `MemoryController`, `BgWorkManager::start_tick`, `BackgroundRunner`, `RegionStatsManager`, and tests all read from the shared `VersionTrack`.

## Risks

Misconfigured thresholds can disable IME, trigger constant eviction, or allow loads to exceed memory budget. Manual capacity is not capped by `MAX_CAPACITY` and does not reduce block-cache capacity, by design, so operator-supplied values carry more risk. Validation uses `unwrap` after earlier initialization checks; new fields or call-order changes should preserve those invariants. The skipped `cross_check_interval` is test-only and should not be enabled in production. Online updates bypass this file's startup `validate` path unless the broader config system enforces equivalent validation.

## Test Signals

`test_validate` verifies disabled defaults, valid manual settings, GC interval bounds, derived threshold deltas for 1 GiB and 5 GiB capacities, smaller region split effects, auto-disable for insufficient derived capacity, manual override behavior, block-cache reduction for derived capacity, max derived capacity clamp, and no block-cache reduction for manual over-max capacity.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/cross_check.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/src/cross_check.rs

## Purpose

Provides a periodic consistency auditor for test/debug use. It compares in-memory engine snapshots against RocksDB snapshots under MVCC snapshot semantics, allowing only differences that are valid because IME GC, RocksDB/TiKV GC, rollback/lock writes, delete markers, or region metadata changes have occurred.

## Important APIs, Types, And Functions

`CrossChecker` owns a PD client, `RegionCacheMemoryEngine`, `RocksEngine`, check interval, and a callback for TiKV's safe point. `StopReason` reports non-panic early exits: `RegionMetaChanged`, `KeyGcInRocksDB`, and `TiKVSafepointGetFailed`. `CrossCheckTask::CrossCheck` is the timer task. The main method `cross_check_region` compares `CF_LOCK` and `CF_WRITE` between a `RegionCacheSnapshot` and `RocksSnapshot`. Helpers `check_with_key_in_disk_iter`, `check_remain_disk_key`, and `check_duplicated_mvcc_version_for_last_user_key` implement alignment and validity rules. `KeyCheckingInfo` records MVCC versions for one user key and the latest version at or below the active safe point.

## Control Flow

On each timer, `run` collects active regions, takes one RocksDB snapshot, asks PD for a TSO, chooses a read timestamp one minute in the past, and builds IME snapshots using the RocksDB snapshot sequence number. It then audits each region. For every CF, it creates bounded iterators over the region range. Lock CF must match key/value exactly, because it is not subject to MVCC write-CF filtering. Write CF can diverge only in narrowly checked ways: rollback and lock writes may be absent, versions below the IME safe point may be filtered when a newer retained version or delete marker makes them invisible, and in-memory keys absent from disk can stop the check if TiKV's global safe point implies RocksDB already GCed them.

The checker advances the disk iterator until it aligns with the current memory key. Each skipped disk key is parsed as a `WriteRef` and checked against the current safe point, current/previous user-key MVCC recordings, delete-marker state, and region metadata. If a disk key newer than the safe point is missing from IME, or a lower version below the safe point was filtered without a valid retaining version/delete marker, the checker panics. For write-CF `Put` entries without short values, it also validates that the corresponding default-CF value exists in the memory snapshot.

## State And Persistence Behavior

Cross-checking is read-only. It snapshots RocksDB and IME state, consults the current region safe point from region metadata, and may refresh that safe point during comparison. It does not repair state or persist results; failures are expressed as panics for invariant violations or logged stop reasons for expected races/GC cases.

## Dependencies And Integration Points

Started by `BackgroundTask::TurnOnCrossCheck` in `background.rs` when `InMemoryEngineConfig.cross_check_interval` is nonzero. It depends on `engine_traits` iterators and cache snapshots, `engine_rocks`, PD TSO, `txn_types::{Key, TimeStamp, WriteRef, WriteType}`, `background::{split_ts, parse_write}`, and the local read snapshot/iterator implementation. `RegionCacheMemoryEngine::start_cross_check` is the external entry point.

## Risks

The auditor intentionally panics on mismatches, so enabling it outside controlled test/debug contexts can crash a process. It assumes sorted MVCC iteration and exact lock-CF parity. Safe points can move while auditing; region splits or evictions are handled as stop reasons, but other races may make failures difficult to interpret. TiKV safe-point callback absence or stale values can cause false positives/early exits. The logic is complex around delete markers and duplicated versions; future GC/filter changes must update the checker in lockstep.

## Test Signals

`test_cross_check` covers many legal divergence patterns, including rollback, delete-marker filtering, retained latest versions below safe point, temporary GC states, and user-key transitions. `test_keys_are_gced_in_rocksdb` verifies early stop when RocksDB has already GCed keys under TiKV safe point. Multiple `#[should_panic]` tests cover missing valid MVCC versions, missing newer keys, redundant IME keys, and invalid rollback/delete scenarios. These tests are the primary regression suite for checker semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/cross_check.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/engine.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/src/engine.rs

## Purpose

Defines the in-memory region cache engine and its core storage abstraction. It mirrors selected RocksDB region data into three global skiplist CFs, exposes TiKV `RegionCacheEngine`/`RegionCacheEngineExt` behavior, handles region lifecycle events, and connects foreground writes to background loading/deletion.

## Important APIs, Types, And Functions

`cf_to_id`, `id_to_cf`, and `is_lock_cf` map TiKV CF names to skiplist indexes. `SkiplistHandle` wraps a `crossbeam_skiplist::SkipList<InternalBytes, InternalBytes>` and provides guarded `get`, `get_with_user_key`, `insert`, `remove`, iterator, and size access. `SkiplistEngine` owns the three CF skiplists for default, lock, and write data; `delete_range_cf` and `delete_range` remove all entries for a `CacheRegion`, using non-MVCC boundaries for lock CF and MVCC boundaries for default/write CFs.

`RegionCacheMemoryEngineCore` owns `SkiplistEngine` and `RegionManager`. Its `prepare_for_apply` is the key foreground gate: it decides whether a region is cached, loading, pending, evicted, outdated, or absent; updates `being_written` flags; and schedules background load from a RocksDB snapshot when a pending region first transitions to loading. `RegionCacheMemoryEngine` owns the core, background manager, optional `RocksEngine`, memory controller, statistics, config, and lock-CF tombstone byte counter. Public methods include `new`, `with_region_info_provider`, `new_region`, `load_region`, `evict_region`, `bg_worker_manager`, `memory_controller`, `statistics`, and `start_cross_check`.

## Control Flow

Construction requires `config.value().enable`, creates a shared core and `MemoryController`, then starts `BgWorkManager` with optional region info and raft casual router. `set_disk_engine` stores the RocksDB handle and notifies the background runner. `snapshot` delegates to `RegionCacheSnapshot::new`, which verifies region/read constraints in the read module.

When foreground apply calls `prepare_for_apply`, the fast path reads region metadata and returns `Cached`, `Loading`, or `NotInCache` without write-locking if possible. The slow path handles pending regions, outdated epoch versions, flashback cancellation, and scheduling of `BackgroundTask::LoadRegion`. The method captures the RocksDB snapshot only after dropping region-manager locks to avoid long lock holds. Region events drive state transitions: `Eviction` calls `evict_region` and schedules deletion for immediately deletable regions, `TryLoad` optionally respects manual load ranges, `Split` delegates to `RegionManager::split_region`, and `EvictByRange` evicts all overlapped cached regions.

## State And Persistence Behavior

All cache data is volatile skiplist state. The durable source of truth remains the disk engine. Region metadata records cache state, epochs, ranges, snapshots, writes in progress, eviction reasons, and safe points. Eviction makes a region unreadable immediately through metadata, but data may remain in skiplists until delayed delete-range work can safely run. Writes are mirrored through `write_batch.rs` and must attach `MemoryController` handles to inserted `InternalBytes` so memory is released on drop.

## Dependencies And Integration Points

Depends on `crossbeam_skiplist`, crossbeam epoch guards, `engine_rocks::RocksEngine`, `engine_traits` region cache traits and CF constants, `pd_client`, raftstore `RegionInfoProvider`/`CasualRouter`, local `background`, `keys`, `memory_controller`, `read`, `region_manager`, and `statistics`. It is the primary type re-exported by `lib.rs` as `RegionCacheMemoryEngine`.

## Risks

The region state machine is central and race-prone: pending regions can become outdated, split, flashback-canceled, evicted, or loaded while writes are in flight. `prepare_for_apply` unwraps `rocks_engine` when scheduling load, so callers must set a disk engine before loading can actually occur. Skiplist delete boundaries differ by CF; using the wrong boundary encoding can delete too much or leak keys. Deletion is eventual, so memory may remain above thresholds until snapshots/writes/GC release. Public `must_set_region_state` is benchmark-only and bypasses normal invariants.

## Test Signals

Tests verify outdated epoch overlap handling, delete-range behavior for default/write and lock CFs, active/inactive region transitions across split and eviction, and eviction callbacks blocked by active snapshots. These tests complement background and write-batch failpoint tests that exercise the same engine state machine.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/engine.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/keys.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/src/keys.rs

## Purpose

Defines the internal key/value byte wrapper and encoding scheme used by the in-memory engine skiplists. The format mirrors RocksDB internal-key ordering while preserving TiKV MVCC keys inside the user-key portion.

## Important APIs, Types, And Functions

`InternalBytes` wraps `bytes::Bytes` and an optional `Arc<MemoryController>`. When dropped with a controller set, it releases `bytes.len() + MEM_CONTROLLER_OVERHEAD`. It exposes constructors, raw byte accessors, `same_user_key_with`, `set_memory_controller`, and `memory_size_required`. Its `Ord` implementation compares all bytes except the final eight-byte internal suffix lexicographically, then compares the suffix as little-endian `u64` in descending order.

`ValueType` is the internal value/deletion tag with `Deletion = 0` and `Value = 1`. `VALUE_TYPE_FOR_SEEK` and `VALUE_TYPE_FOR_SEEK_FOR_PREV` match RocksDB seek conventions. `InternalKey` is the decoded view `{ user_key, v_type, sequence }`. `encode_internal_bytes`, `encode_key`, `encode_seek_key`, and `encode_seek_for_prev_key` append an eight-byte little-endian suffix containing `(seq << 8) | value_type`. `decode_key` reverses that encoding. Boundary helpers produce region start/end keys with or without MVCC timestamps, and `encoding_for_filter` builds a default-CF key for a MVCC prefix plus start timestamp.

## Control Flow

Keys inserted into skiplists are constructed from an MVCC user key plus sequence/value-type suffix. Default/write CF region scans use `encode_key_for_boundary_with_mvcc`, which appends `TimeStamp::max()` to the region boundary so all MVCC versions for the region start are included and the region end is excluded. Lock CF scans use `encode_key_for_boundary_without_mvcc`, because lock keys do not carry MVCC versions. GC filtering uses `encoding_for_filter` to find default-CF entries that correspond to write-CF `Put` records with external values.

## State And Persistence Behavior

`InternalBytes` is the memory-accounting ownership unit for skiplist keys and values. The source bytes are immutable and reference-counted, but memory quota is released when the wrapper drops, before the underlying `Bytes` allocation may actually be freed. The encoded keys are volatile in-memory representations; they are derived from RocksDB/MVCC keys and are not persisted by this module.

## Dependencies And Integration Points

Uses `bytes::{Bytes, BufMut}`, `engine_traits::CacheRegion`, `txn_types::{Key, TimeStamp}`, local `MemoryController`, and write-batch memory overhead constants. All storage, read, write, GC, load, cross-check, and delete-range code depends on this encoding for ordering and boundary correctness.

## Risks

The suffix format allows `u64::MAX` only as a sentinel; otherwise sequences must fit in 56 bits. `decode_key` unwraps value-type conversion and asserts minimum length, so corrupt internal keys panic. Ordering correctness depends on TiKV MVCC keys already being in memory-comparable encoded form. Memory accounting can be wrong if inserted keys/values do not have `memory_controller` set; `SkiplistHandle::insert` asserts this for normal writes.

## Test Signals

`test_compare_key` verifies value-type ordering, descending sequence ordering, MVCC timestamp ordering, and sentinel behavior. `test_encode_decode` checks little-endian suffix layout, sequence extraction, and value-type extraction. Test-only constructors generate deterministic user, region, MVCC, and value bytes for broader module tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/keys.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/lib.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/src/lib.rs

## Purpose

Crate root for TiKV's in-memory engine component. It declares internal modules, exposes the public API surface used by TiKV integration code and tests, and defines `InMemoryEngineContext`, the construction bundle for config, statistics, and PD access.

## Important APIs, Types, And Functions

The crate enables nightly features `core_intrinsics`, `slice_pattern`, and `str_as_str`, then declares modules for background work, config, cross-checking, engine, keys, memory control, metrics, performance context, reads, region labels/managers/stats, statistics, tests, and write batches. Re-exports include `BackgroundRunner`, `BackgroundTask`, `GcTask`, `InMemoryEngineConfig`, `RegionCacheMemoryEngine`, `SkiplistHandle`, key helpers/types, `flush_in_memory_engine_statistics`, `RegionCacheSnapshot`, `RegionCacheStatus`, `RegionState`, `Statistics as InMemoryEngineStatistics`, and `RegionCacheWriteBatch`.

`InMemoryEngineContext` stores `Arc<VersionTrack<InMemoryEngineConfig>>`, `Arc<InMemoryEngineStatistics>`, and `Arc<dyn PdClient>`. `new` accepts real config and PD client. `new_for_tests` installs a mock PD client whose `get_tso` returns a composed physical-now timestamp. Accessors expose cloned PD/statistics handles and a config reference.

## Control Flow

Consumers create `InMemoryEngineContext`, pass it into `RegionCacheMemoryEngine::new` or `with_region_info_provider`, and the engine extracts config/statistics/PD client during construction. Test code can avoid external PD setup through `new_for_tests`.

## State And Persistence Behavior

The crate root holds no storage state beyond the context wrapper. `InMemoryEngineContext` is cloned by value and shares all underlying state through `Arc`s. Statistics are initialized with `Arc::default()` and then shared with engine/metrics flushing.

## Dependencies And Integration Points

Uses `pd_client::PdClient`, `tikv_util::config::VersionTrack`, `txn_types::TimeStamp`, and `futures::future::ready` for the test PD client. It is the public entry point tying together the local modules reviewed in this subset and the rest of TiKV.

## Risks

The public re-export list defines what downstream code can rely on; changing it can break integration tests or TiKV call sites. `new_for_tests` only implements `get_tso`, so tests that require other PD methods must use a richer mock. Nightly feature gates tie this crate to a compiler/runtime environment that supports those internal features.

## Test Signals

No direct tests are in `lib.rs`, but every module test using `InMemoryEngineContext::new_for_tests`, `RegionCacheMemoryEngine`, re-exported key helpers, snapshots, and write batches exercises this public API surface.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/memory_controller.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/src/memory_controller.rs

## Purpose

Tracks and limits in-memory engine memory usage using exact allocated key/value byte counts plus estimated skiplist node overhead, and exposes threshold checks used by writes, loads, and eviction scheduling.

## Important APIs, Types, And Functions

`MemoryUsage` reports `NormalUsage(usize)`, `EvictThresholdReached(usize)`, or `CapacityReached(usize)`. `MemoryController` stores an atomic `allocated` byte count, shared `VersionTrack<InMemoryEngineConfig>`, a `memory_checking` flag, and the `SkiplistEngine` used for node-count overhead. `new` constructs the controller. `acquire` attempts to reserve bytes and returns a threshold/capacity result, rolling back the reservation when capacity would be exceeded. `release` subtracts bytes. `reached_stop_load_threshold`, `stop_load_threshold`, `evict_threshold`, `set_memory_checking`, `memory_checking`, and `mem_usage` expose threshold and current-usage state.

## Control Flow

Writers/loaders call `acquire(n)` before inserting key/value wrappers into the skiplist. The method adds `n`, computes total memory as allocated bytes plus `skiplist_engine.node_count() * NODE_OVERHEAD_SIZE_EXPECTATION`, and compares it to live config thresholds. If the capacity would be reached, it subtracts `n` and returns `CapacityReached(previous_usage)`. If only the eviction threshold is reached, it keeps the reservation and returns `EvictThresholdReached`. Inserted `InternalBytes` later call `release` on drop, returning their accounted size.

## State And Persistence Behavior

All state is volatile and process-local. `allocated` intentionally excludes skiplist node overhead, which is recomputed from current node count. Because config is read from `VersionTrack` on each call, online capacity/threshold changes take effect without rebuilding the controller.

## Dependencies And Integration Points

Depends on `InMemoryEngineConfig`, `SkiplistEngine`, and `write_batch::NODE_OVERHEAD_SIZE_EXPECTATION`. It is created by `RegionCacheMemoryEngine`, passed into `BgWorkManager`, used by write batches and background loading/filtering, and embedded indirectly in `InternalBytes` for release-on-drop.

## Risks

Memory accounting is approximate and relaxed-atomic; it is designed for threshold control rather than byte-perfect enforcement. Concurrent `acquire` calls can temporarily observe stale node counts or threshold values. A bad `release` call with an incorrect size would underflow the atomic counter. The capacity check uses `>=`, so equal-to-capacity acquisitions are rejected and return the usage before the attempted allocation.

## Test Signals

`test_memory_controller` verifies normal, eviction-threshold, and capacity results; rollback of failed capacity acquisition; release behavior; node-overhead contribution after a skiplist insert; and threshold behavior after a node is removed.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/memory_controller.rs -->
