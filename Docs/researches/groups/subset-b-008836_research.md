# Group Research: subset-b-008836

This grouped report covers TiKV in-memory engine files under `sources/storage-engines/tikv/components/in_memory_engine/src/`. Each section is delimited for reconciliation into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/memory_usage_test.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/src/memory_usage_test.rs

## Purpose

This file contains ignored, heavy memory amplification tests for representative TiDB index records stored in the in-memory engine write CF. It is not part of normal daily CI; the file documents a manual release-mode command and prints allocator deltas so maintainers can estimate resident memory overhead versus logical row/index payload size.

## Important APIs, Types, And Functions

- `Case` describes one benchmark case: name, encoded key, optional write value, logical bytes per key, and total logical target size.
- `test_memory_usage_two_fields_secondary_index_two_fields_clustered_index` builds a secondary-index style key with no value and a 29-byte logical payload assumption.
- `test_memory_usage_two_fields_unique_index_two_fields_clustered_index` builds a unique-index style write record with an encoded common-handle value.
- `evaluate_memory_usage` performs the actual population loop, reads allocator stats with `tikv_alloc::fetch_stats`, and reports amplification ratios.

## Control Flow

Each ignored test prepares a real encoded key/value case, then calls `evaluate_memory_usage`. The evaluator creates a test skiplist engine via `new_skiplist_engine_for_test`, captures starting allocator stats, repeatedly appends a unique MVCC timestamp to the key, encodes a `Write::new(WriteType::Put, commit_ts, value)` payload, and inserts it into `CF_WRITE`. After enough records approximate the configured logical total, it captures end allocator stats and prints resident-memory amplification plus per-allocator-stat deltas.

## State And Persistence Behavior

All state is in-memory skiplist state. No RocksDB persistence is used, and the test explicitly drops the skiplist after printing results. Memory accounting depends on allocator resident stats rather than engine metadata, so results are process- and allocator-sensitive.

## Dependencies And Integration Points

The test depends on `engine_traits::CF_WRITE`, `txn_types::{Key, Write, WriteType}`, `tikv_util::config::ReadableSize`, `hex`, `tikv_alloc`, and `crate::prop_test::new_skiplist_engine_for_test`. It integrates with the in-memory engine through its CF handle and with the internal key/value memory controller wrapper supplied by the property-test helper.

## Risks And Edge Cases

The tests are deliberately ignored because they insert about 200 MiB of logical data and rely on allocator resident statistics, which can vary by platform, build mode, allocator fragmentation, and other threads. The secondary-index and unique-index examples are hard-coded snapshots of TiDB encoding expectations; if upstream key/value formats change, the amplification scenario may become stale. The loop includes index `0..=logical_size_in_total / logical_size_pre_key`, so it intentionally overshoots the logical target by one record.

## Test Signals

The file itself is test-only. Its useful signal is manual printed amplification, not pass/fail assertions beyond successful insertion and allocator-stat lookup. It complements unit/property tests by measuring operational memory behavior for realistic key shapes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/memory_usage_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/metrics.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/src/metrics.rs

## Purpose

This file defines Prometheus metrics and static auto-flush wrappers for the in-memory engine. It bridges internal ticker/statistics counters, eviction reasons, GC filtering, memory usage, load/write latencies, auto-load/evict observations, and per-CF operation counts into TiKV's metrics surface.

## Important APIs, Types, And Functions

- Static label enums model GC count types, ticker names, eviction reasons, operation types, and the three TiKV CFs.
- Lazy statics register gauges, counters, counter vecs, histograms, and histogram vecs under `tikv_in_memory_engine_*` names plus `tikv_safe_point_gap_with_in_memory_engine`.
- `flush_in_memory_engine_statistics` drains global `InMemoryEngineStatistics` ticker counters and forwards them to metric counters.
- `flush_engine_ticker_metrics` maps `Tickers` variants to flow/locate metric labels.
- `observe_eviction_duration` maps every `engine_traits::EvictReason` variant to the matching eviction-duration label.
- `count_operations_for_cfs` records put/delete counts for default, lock, and write CFs.

## Control Flow

Metrics are registered at first lazy-static access. Runtime code records low-cost local static metrics and periodically calls flush helpers. `flush_in_memory_engine_statistics` iterates `ENGINE_TICKER_TYPES`, atomically drains each ticker through `get_and_reset_ticker_count`, then dispatches the value by match. Eviction completion calls `observe_eviction_duration`, and write accounting calls `count_operations_for_cfs` with fixed CF-indexed arrays.

## State And Persistence Behavior

Metrics are process-local Prometheus state; no persistent state is maintained. `flush_in_memory_engine_statistics` is destructive for ticker counters because it resets them after reading, while gauges and histograms retain standard Prometheus in-process state.

## Dependencies And Integration Points

The file depends on `prometheus`, `prometheus_static_metric`, `lazy_static`, `engine_traits::EvictReason`, and local `statistics::{Tickers, ENGINE_TICKER_TYPES}`. It is integrated by read iterators, region eviction completion, memory-controller/reporting code, GC/load/write paths, and auto-load/evict policy code in `region_stats.rs`.

## Risks And Edge Cases

The match in `flush_engine_ticker_metrics` treats any ticker outside `ENGINE_TICKER_TYPES` as unreachable, so the ticker list and enum mapping must stay synchronized. `count_operations_for_cfs` asserts both arrays have length three and relies on `cf_to_id` ordering: default, lock, write. Any new `EvictReason` requires adding a static label and match arm or compilation will fail. Static metric registration uses `unwrap`, so duplicate metric names would panic at initialization.

## Test Signals

There are no local tests in this file. Coverage comes indirectly from read-flow tests in `read.rs`, statistics tests in `statistics.rs`, and eviction paths in `region_manager.rs`/`region_stats.rs` that exercise metric update paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/perf_context.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/src/perf_context.rs

## Purpose

This file provides a thread-local performance context compatible with RocksDB-style read metrics. It collects per-thread byte and internal-skip counters for in-memory engine gets and iterators without forcing every hot operation through global atomics.

## Important APIs, Types, And Functions

- `PERF_CONTEXT` is a `thread_local!` `RefCell<PerfContext>`.
- `PerfContext` holds `get_read_bytes`, `iter_read_bytes`, `internal_key_skipped_count`, and `internal_delete_skipped_count`.
- `perf_counter_add!` increments a named field in the current thread's context.

## Control Flow

Read code imports `PERF_CONTEXT` and the exported macro. Point reads increment `get_read_bytes` after returning a visible value. Iterators aggregate local read bytes in `LocalStatistics`, and on drop add the iterator byte count to `iter_read_bytes`; iterator traversal also increments internal key/delete skip counters during MVCC visibility filtering.

## State And Persistence Behavior

State is per-thread and in-memory only. It is not automatically reset by this file, so callers/tests that compare deltas must account for prior operations on the same thread. The `RefCell` provides interior mutability in single-thread-local scope, not cross-thread sharing.

## Dependencies And Integration Points

The module depends only on `std::cell::RefCell`. Its macro is used heavily by `read.rs`, and `RegionCacheIterMetricsCollector` exposes selected fields through `engine_traits::IterMetricsCollector`.

## Risks And Edge Cases

Because counters are thread-local, aggregating across worker threads requires external collection logic. The macro assumes the supplied identifier is an existing `PerfContext` field, so renames are compile-time breaking changes. Tests that do not reset the context may be order-sensitive if run on the same test thread and assert absolute values.

## Test Signals

`read.rs` contains direct assertions for `get_read_bytes`, `iter_read_bytes`, and skip counters, including comparisons with RocksDB statistics in `test_read_flow_metrics` and tombstone counting in `test_tombstone_count_when_iterating`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/perf_context.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/prop_test.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/src/prop_test.rs

## Purpose

This file property-tests the skiplist-backed in-memory engine against RocksDB for basic put/get/delete/scan/delete-range behavior across default, lock, and write CFs. It also provides `new_skiplist_engine_for_test`, a shared helper used by other test modules.

## Important APIs, Types, And Functions

- `new_skiplist_engine_for_test` creates a `SkiplistEngine`, a high-capacity `MemoryController`, and a closure that encodes raw key/value inputs into `InternalBytes` with controller ownership and an epoch guard.
- `Operation` models generated mutations and reads.
- `gen_operations` generates CF plus operation vectors with bounded key/value sizes.
- `scan_rocksdb` and `scan_skiplist` normalize scan results for comparison.
- `test_rocksdb_skiplist_basic_operations` replays generated operations against RocksDB and the skiplist and asserts equivalent visible results.

## Control Flow

The property test generates a CF and up to 100 operations. For default/write CFs it appends a fixed MVCC suffix to raw keys before writing both engines, because skiplist delete-range semantics account for MVCC suffixes. Puts insert into RocksDB and the skiplist; gets compare RocksDB optional value with skiplist lookup; scans seek both engines and compare ordered key/value vectors; delete-range normalizes range endpoints, constructs a `CacheRegion`, deletes from skiplist, then deletes the MVCC-suffixed range from RocksDB.

## State And Persistence Behavior

RocksDB state lives in a temporary directory and is discarded. Skiplist state is memory-only and protected by crossbeam epoch guards. The helper configures very high test capacity/evict thresholds to keep memory-control behavior from interfering with correctness comparisons.

## Dependencies And Integration Points

The file depends on `engine_rocks`, `engine_traits`, `proptest`, `crossbeam::epoch`, `txn_types`, `tikv_util::config::VersionTrack`, local key encode/decode helpers, `MemoryController`, and `SkiplistEngine`. `memory_usage_test.rs` also imports `new_skiplist_engine_for_test`.

## Risks And Edge Cases

The generated get/delete/scan keys can be empty even though put keys are non-empty; this intentionally probes boundary behavior but does not cover all TiKV key encoding invariants. The fixed `MVCC_SUFFIX` means generated tests compare one simplified MVCC shape. Delete-range behavior differs by CF and depends on correct endpoint ordering after swapping `k1` and `k2`.

## Test Signals

The proptest runs 100 generated cases and there is a fixed regression `test_case1` for a prior delete-range/scan interaction in write CF. This is a high-value behavioral oracle for low-level skiplist operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/prop_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/read.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/src/read.rs

## Purpose

This file implements snapshot reads and RocksDB-like iteration over the in-memory region cache. It enforces region boundaries, region epoch/safe-point validation, sequence-number visibility, tombstone handling, prefix iteration, read metrics, and delayed physical eviction while snapshots are alive.

## Important APIs, Types, And Functions

- `MAX_SEQUENCE_NUMBER` is the highest sequence used for seek construction.
- `RegionCacheSnapshotMeta` records the `CacheRegion`, read timestamp, and shared RocksDB/in-memory sequence number.
- `RegionCacheSnapshot::new` registers a region snapshot with `RegionManager` and captures the skiplist engine.
- `Drop for RegionCacheSnapshot` unregisters the snapshot and schedules `BackgroundTask::DeleteRegions` for ranges that become physically removable.
- `Iterable for RegionCacheSnapshot::iterator_opt` creates `RegionCacheIterator` with mandatory lower/upper bounds checked against the snapshot region.
- `Peekable for RegionCacheSnapshot::get_value_cf_opt` performs bounded point lookup by encoded internal seek key and sequence visibility.
- `RegionCacheIterator` implements forward/backward iteration, prefix-restricted seeks, direction reversal, sequence filtering, deletion skipping, statistics flushing, and `MetricsExt`.
- `RegionCacheDbVector` wraps `bytes::Bytes` as an engine `DbVector`.

## Control Flow

Snapshot construction first calls `region_manager.region_snapshot`, which rejects non-active, epoch-mismatched, or too-old reads. Point get checks the user key is within the cached region, seeks the CF skiplist to `encode_seek_key(key, sequence_number)`, decodes the found internal key, and returns only visible `Value` entries for the exact user key.

Iterator construction requires both bounds and rejects bounds outside the region. Forward seek uses `encode_seek_key` and `find_next_visible_key`, which walks until it finds the first visible non-deleted version for a new user key within upper bound and optional prefix. Backward seek uses `encode_seek_for_prev_key`, `prev_internal`, `find_value_for_current_key`, and `find_user_key_before_saved` to collect the latest visible value while scanning reverse through versions. `next` and `prev` handle direction reversal so callers can alternate directions in RocksDB-compatible ways. On iterator drop, local counters are flushed into global `Statistics` and thread-local `PERF_CONTEXT`.

## State And Persistence Behavior

The module does not persist data. It reads crossbeam-skiplist CFs owned by `SkiplistEngine`, tracks active read snapshots in `RegionManager`, and schedules asynchronous delete-range work when snapshot release unblocks eviction. Sequence numbers are shared with disk engine snapshots to preserve atomic write visibility across memory and RocksDB.

## Dependencies And Integration Points

The file depends on `engine_traits` snapshot/iterator/read traits, `crossbeam_skiplist`, `crossbeam::epoch`, `engine_rocks` prefix transforms, local key encoding/decoding, `RegionCacheMemoryEngine`, `BackgroundTask`, `metrics::IN_MEMORY_ENGINE_SEEK_DURATION`, `statistics`, and `perf_context`. It is the main read surface used by the engine implementation and by tests comparing behavior to RocksDB.

## Risks And Edge Cases

Iterator correctness is sensitive to internal-key ordering, sequence comparison, deletion semantics, and direction reversal. Prefix seek asserts key length at least eight bytes and disables `seek_to_first/last` via assertions when prefix mode is enabled. `iterator_opt` only supports explicit bounds; callers that omit bounds receive `Error::BoundaryNotSet`. Snapshot drops can schedule background deletion, so failures in the background scheduler leave eviction cleanup dependent on shutdown assertions/logging. `find_user_key_before_saved` calls `self.is_visible(self.sequence_number)`, which is always true for normal sequence numbers and functions as unconditional skip accounting rather than filtering the current entry.

## Test Signals

The test module is extensive: snapshot refcounts and safe points, point get with sequence-visible deletions, forward and backward iteration with bounds, sequence visibility in both directions, user-key skip corner cases, prefix seek, skiplist range eviction, eviction with/without active snapshots after split, tombstone/perf counters, read-flow metrics compared to RocksDB statistics, RocksDB iterator compatibility cases, newer-sequence behavior, and direction reversal.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/read.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/region_label.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/src/region_label.rs

## Purpose

This file watches PD region-label rules and keeps an in-memory rule map used to identify key ranges that should always be cached by the in-memory engine. It models the subset of PD label-rule JSON relevant to key-range cache labels.

## Important APIs, Types, And Functions

- `RegionLabel`, `LabelRule`, and `KeyRangeRule` mirror PD labeler JSON structures.
- `TryFrom<&KeyRangeRule> for CacheRegion` decodes TiDB hex keys and converts them to data-key/data-end-key cache ranges.
- `RegionLabelRulesManager` stores rules in a `DashMap` and invokes an optional change callback on add/remove.
- `RegionLabelServiceBuilder` wires a manager, PD RPC client, optional rule filter, and cluster id.
- `RegionLabelService::watch_region_labels` loads all rules, then watches PD meta storage for put/delete events.
- `reload_all_region_labels` performs a full prefixed get with retry.

## Control Flow

The service computes a PD meta-storage path from cluster id and `REGION_LABEL_PATH_PREFIX`. Startup calls `reload_all_region_labels`, parsing each JSON value as a `LabelRule` and applying the optional filter before adding it. The watch loop opens a prefixed watch from the last revision with previous KV data. Put events parse the new value and call `on_label_rule_add`; delete events parse `prev_kv` and call `on_label_rule_delete`. Data compaction triggers a full reload and watch restart. Other PD/watch errors log, wait one second through `GLOBAL_TIMER_HANDLE`, abort the stream, and retry.

## State And Persistence Behavior

Local state is the manager's in-memory `DashMap` plus the service's current watch revision. Durable rule storage is external PD meta storage. Duplicate identical put events are detected and ignored for callback purposes, but remove events always call the callback if configured.

## Dependencies And Integration Points

The file depends on `pd_client` meta-storage APIs, `kvproto::meta_storagepb::EventEventType`, `dashmap`, `serde_json`, `futures`, `keys::{data_key, data_end_key}`, `engine_traits::CacheRegion`, and TiKV logging/timer utilities. The callback is the integration hook for cache load/evict policy when labels change.

## Risks And Edge Cases

Invalid hex in `KeyRangeRule` or malformed JSON prevents conversion/application and only logs parse errors in watch/reload paths. The service loops forever and relies on task cancellation by its owner. Watch revision handling uses response-header revisions; compaction is handled, but missed deletes before reload could leave stale local rules until the full reload completes. `path_suffix` exists but is only internally set to `None` by the builder in this file.

## Test Signals

Tests include a disabled local PD debugging test and mock-PD CRUD/watch tests. Helpers create label rules, insert/delete through PD meta storage, and assert the manager observes additions and removals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/region_label.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/region_manager.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/src/region_manager.rs

## Purpose

This file owns cached-region metadata, the region cache state machine, active snapshot tracking, split/epoch handling, manual load ranges, and eviction eligibility. It is the coordination layer that keeps foreground reads, raftstore region events, GC, writes, and background delete-range tasks consistent.

## Important APIs, Types, And Functions

- `RegionState` models `Pending`, `Loading`, `Active`, `LoadingCanceled`, `PendingEvict`, and `Evicting`, with validated state transitions.
- `SnapshotList` tracks active snapshot read timestamps and reference counts.
- `CacheRegionMeta` stores a `CacheRegion`, safe point, state, snapshot list, GC/write flags, eviction info/callback, and smoothed coprocessor request state.
- `RegionMetaMap` indexes active metadata by range end key and region id, detects overlaps, manages manual load ranges, and admits new loads.
- `RegionManager` wraps `RegionMetaMap`, historical split regions with live snapshots, a single-GC-task flag, and an active fast-path flag.
- `LoadFailedReason` distinguishes overlap, pending range, and evicting conflicts, including whether the same region caused the failure.
- `RegionCacheStatus` summarizes public cache status values.

## Control Flow

Loads enter `RegionMetaMap::load_region`, which rejects overlaps or same-id conflicts unless stale pending metadata can be removed. Snapshots call `region_snapshot`, requiring an active matching-epoch region and `read_ts > safe_point`, then increment the snapshot list. Dropping a snapshot calls `remove_region_snapshot`, which decrements either current metadata or historical split metadata and returns regions whose pending eviction is no longer blocked.

Eviction starts with `evict_region`, resolving the exact region or all overlapped regions. Pending regions are removed immediately; active regions become `PendingEvict`; loading regions become `LoadingCanceled`; already-evicting states are ignored. If no current or historical snapshots overlap, `PendingEvict` advances to `Evicting` and the caller receives ranges that can be physically deleted. `on_delete_regions` removes metadata, observes eviction duration, and runs completion callbacks. Splits remove the source region, derive child metadata preserving safe point/state/flags, and move the source to `historical_regions` if old snapshots still exist.

## State And Persistence Behavior

All metadata is memory-resident. The authoritative persisted data remains in RocksDB and the skiplist cache contents are cleaned asynchronously by background delete-range tasks. `historical_regions` is a temporary in-memory structure that prevents deletion of split descendants while pre-split snapshots remain alive. `is_active` is an atomic fast-path signal for whether any region metadata exists.

## Dependencies And Integration Points

The manager depends on `engine_traits::{CacheRegion, EvictReason, FailedReason, OnEvictFinishedCallback}`, `parking_lot::RwLock`, standard mutex/atomics, `tikv_util::smoother::Smoother`, local metrics, and `read::RegionCacheSnapshotMeta`. It is called by snapshot creation/drop in `read.rs`, raftstore/apply event handling in the engine, GC/write paths, memory-pressure eviction, region stats policy, and background deletion completion.

## Risks And Edge Cases

Correctness relies on strict state-transition assertions and non-overlapping range invariants. Stale pending epochs can be replaced only when containment rules hold; same-id non-overlapping conflicts are rejected for implementation simplicity. Active snapshots and historical regions can delay physical eviction and memory release. `on_delete_regions` unwraps eviction info and asserts epoch matches, so callers must only pass regions that reached `Evicting`. Manual load ranges are stored as a vector with union/difference logic that must preserve non-overlap expectations without sorting guarantees.

## Test Signals

Tests cover snapshot safe-point checks, split with historical snapshots, eviction readiness, load conflict reasons, same-id overlap behavior, multi-region eviction, and manual load range overlap/add/remove cases. The `Drop` check on `RegionMetaMap` verifies range and id indexes remain consistent in tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/region_manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/region_stats.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/src/region_stats.rs

## Purpose

This file implements the policy layer for automatic region loading and eviction based on raftstore region activity, memory-controller thresholds, and smoothed coprocessor request rates. It chooses top regions to load and low-value cached regions to evict.

## Important APIs, Types, And Functions

- `RegionStatsManager` holds config, a `RegionInfoProvider`, a concurrency flag, region load timestamps, eviction minimum duration, and last check time.
- `ready_for_auto_load_and_evict` and `complete_auto_load_and_evict` throttle and serialize policy runs.
- `collect_regions_to_load_and_evict` returns regions to load and regions to evict based on top-region stats, cached-region stats, and memory pressure.
- `evict_on_evict_threshold_reached` evicts low-read-flow regions in small batches when memory has crossed the eviction/stop-load threshold.
- `CachedRegionStat` stores region, raw stat, SMA count/average, and iterated count.
- `sort_cached_region_stats` updates each cached region's SMA and sorts by low coprocessor requests, then low iterated count.

## Control Flow

Policy checks are allowed only after a minimum interval and when no check is already running. `collect_regions_to_load_and_evict` first queries stats for cached regions, estimates how many regions can fit before the evict threshold using expected region size, then asks raftstore for that many top regions. Top regions not already cached become load candidates and are recorded with load timestamps. Cached regions are sorted by low activity. If cached count is too small, no eviction occurs. Under stop-load memory pressure, the policy computes average iterated count and SMA coprocessor requests, then selects at most one tenth of cached regions whose request average and iterated count are much lower than average, whose SMA has enough samples, and whose load timestamp exceeds `evict_min_duration`.

`evict_on_evict_threshold_reached` separately handles direct memory pressure: it filters cached regions to those at or below average SMA request rate, evicts chunks of two via a supplied callback, schedules background delete-range work, waits for eviction-finished callbacks to signal memory release, and stops once memory is below the stop-load threshold.

## State And Persistence Behavior

The manager persists no data. It keeps in-memory timing and SMA state through shared `CopRequestsSma` instances owned by region metadata. Region load timestamps are updated as top regions are observed and cleared when a region is evicted.

## Dependencies And Integration Points

The file depends on `raftstore::coprocessor::RegionInfoProvider`, `pd_client::RegionStat`, `MemoryController`, `VersionTrack<InMemoryEngineConfig>`, `BackgroundTask` scheduling, `engine_traits::{CacheRegion, EvictReason, OnEvictFinishedCallback}`, and metrics histograms for auto load/evict observations. It consumes cached-region SMA handles from `RegionMetaMap::cached_regions` and calls `RegionManager` eviction through injected closures.

## Risks And Edge Cases

The policy is heuristic and workload-sensitive. It assumes post-cache request patterns remain representative and deliberately avoids using low MVCC amplification alone as an eviction reason for cached regions. Region stat provider failures log and assert shutdown in non-test mode, returning no changes. Timestamps for newly observed top regions can delay eviction even if a region becomes idle quickly. Waiting for eviction callbacks avoids tight loops but can stall if callbacks are not invoked.

## Test Signals

Tests use a `RegionInfoSimulator` to validate top-region loading, SMA warm-up, idle-region eviction after sufficient samples and duration, no eviction below memory pressure, eviction callback batching/order under threshold pressure, check throttling, and cached-region sort order.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/region_stats.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/statistics.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/src/statistics.rs

## Purpose

This file implements low-overhead in-memory engine ticker statistics. It uses core-local padded counters to reduce contention for hot read/iterator metrics, then provides aggregate and drain operations for metrics flushing.

## Important APIs, Types, And Functions

- `CoreLocalArray<T>` allocates a power-of-two array of per-core values, at least eight entries.
- `physical_core_id` uses `libc::sched_getcpu` on Linux x86_64 and falls back to `-1` elsewhere.
- `Tickers` enumerates bytes read, iterator bytes read, seek/next/prev counts, and found counts.
- `ENGINE_TICKER_TYPES` lists the tickers exported by metrics flushing.
- `StatisticsData` wraps atomic ticker counters.
- `Statistics` provides `record_ticker`, `get_ticker_count`, and `get_and_reset_ticker_count`.
- `LocalStatistics` accumulates per-iterator counters before a single flush on iterator drop.

## Control Flow

Hot paths call `Statistics::record_ticker`, which selects a core-local shard from the current CPU id or a random shard fallback and performs relaxed atomic addition. Aggregate readers lock `_aggregate_lock` and sum all shards. Drain operations also hold the lock and `swap(0)` every shard for the selected ticker. Iterators avoid per-step atomics by updating `LocalStatistics`, then flushing the totals when dropped.

## State And Persistence Behavior

Statistics are process-local and non-persistent. `get_and_reset_ticker_count` clears the selected counter across all shards, so callers use it for periodic Prometheus delta export. Relaxed atomics are sufficient because counters are approximate telemetry rather than correctness state, while the mutex serializes aggregate/drain operations.

## Dependencies And Integration Points

The module depends on `crossbeam::utils::CachePadded`, `rand`, `libc`, standard atomics and mutexes. It integrates with `metrics.rs` for Prometheus flushing and `read.rs` for point-read and iterator accounting.

## Risks And Edge Cases

The core-local index can be inaccurate after thread migration; this is accepted for performance. Non-Linux or failed `sched_getcpu` paths select random shards, reducing locality. Adding a new `Tickers` variant requires updating `TickerEnumMax`, `ENGINE_TICKER_TYPES`, and `metrics.rs` label mapping. Aggregate locking prevents concurrent drains from interleaving, but relaxed increments can still race with drains in the usual telemetry sense.

## Test Signals

`test_core_local` spawns four threads, records two ticker types, validates aggregate totals, verifies drain values, and confirms counters reset to zero after `get_and_reset_ticker_count`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/statistics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/test_util.rs -->
# sources/storage-engines/tikv/components/in_memory_engine/src/test_util.rs

## Purpose

This file provides test helpers for constructing MVCC data in the in-memory skiplist and RocksDB, plus a helper for building minimal `Region` metadata. It keeps read/write tests focused on behavior rather than repetitive encoding and memory-controller setup.

## Important APIs, Types, And Functions

- `put_data` inserts a write-CF record and, when needed, its default-CF value into skiplist handles.
- `put_data_with_overwrite` inserts the same write record at two sequence numbers pointing to the same default-CF start timestamp, modeling overwrite visibility.
- `put_data_impl` performs the common encoded-key/value construction, memory-controller accounting, and skiplist insertion.
- `put_data_in_rocks` writes equivalent MVCC data into RocksDB for comparison tests.
- `new_region` builds a `kvproto::metapb::Region` with id, start/end keys, and one dummy peer.

## Control Flow

Skiplist helpers create a TiKV data key, append commit timestamp for write CF, encode it as an internal value key with a supplied sequence, attach the shared `MemoryController`, acquire estimated memory for the write-batch entry, and insert into the write handle. If `overwrite_seq_num` is supplied, the write CF entry is inserted again with a second sequence. For non-short values, the helper also writes the default-CF value at `start_ts` with sequence `seq_num + 1`. RocksDB helper writes the corresponding write CF entry and, unless the write type is delete or the value is short, writes default CF.

## State And Persistence Behavior

Skiplist helpers mutate in-memory CF handles and memory-controller counters. RocksDB helper persists to the provided temporary/test Rocks engine. The helpers do not clean up state themselves; tests own engine lifetimes.

## Dependencies And Integration Points

The file depends on `engine_traits::SyncMutable`, `engine_rocks::RocksEngine`, `txn_types::{Key, TimeStamp, Write, WriteType}`, local `keys::{data_key, encode_key, InternalBytes, ValueType}`, `MemoryController`, and `RegionCacheWriteBatchEntry` sizing. It is used by in-memory engine tests that need realistic MVCC write/default CF layouts.

## Risks And Edge Cases

`put_data_impl` uses `seq_num + 1` for default CF, so tests must choose sequence numbers intentionally when modeling snapshot visibility. Memory acquisition return values are ignored, which is acceptable for tests configured with adequate capacity but would hide limiter behavior in low-capacity scenarios. `put_data_in_rocks` uses `data_key(key)` for write CF but raw `key` for default CF, matching the expected test layout; callers must pass the right key shape. `new_region` adds a dummy peer solely to satisfy `CacheRegion::from_region` expectations.

## Test Signals

This is a support module rather than a test suite. Its signal is indirect through read, write-batch, and region-manager tests that use these helpers to construct MVCC fixtures.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/in_memory_engine/src/test_util.rs -->
