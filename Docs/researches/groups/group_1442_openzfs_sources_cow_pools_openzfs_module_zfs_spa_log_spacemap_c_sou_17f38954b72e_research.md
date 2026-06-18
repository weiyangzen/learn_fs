# Group Research: group_1442_openzfs_sources_cow_pools_openzfs_module_zfs_spa_log_spacemap_c_sou_17f38954b72e

Scope checked against `Docs/research_subset_a.md`: `sources/cow-pools/openzfs` is included in subset A. All six listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/spa_log_spacemap.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/spa_log_spacemap.c

## Role

`spa_log_spacemap.c` implements OpenZFS log space maps, an optimization for random-write and random-free workloads that would otherwise append small free records to many per-metaslab space maps every transaction group. Instead of immediately persisting each metaslab's free/alloc changes to its own space map, the feature logs changes into a pool-wide per-TXG space map and keeps unflushed per-metaslab changes in memory until selected metaslabs are flushed.

The file owns the feature's runtime policy: creating per-TXG log space map objects, tracking which metaslabs still depend on old logs, importing/replaying log entries into metaslab unflushed range trees, deciding how many metaslabs to flush each sync, destroying obsolete log space maps, maintaining summary accounting, and exposing module tunables.

## Persistent Structures

The feature uses a MOS ZAP entry named `DMU_POOL_LOG_SPACEMAP_ZAP`, mapping TXG keys to log space map object IDs. `spa_generate_syncing_log_sm()` creates this ZAP on first use, activates `SPA_FEATURE_LOG_SPACEMAP`, allocates the current TXG's space map, inserts it into the ZAP, and opens it as `spa_syncing_log_sm`.

Each top-level vdev can store `VDEV_TOP_ZAP_MS_UNFLUSHED_PHYS_TXGS`, whose object contains one `metaslab_unflushed_phys_t` record per metaslab. `spa_ld_unflushed_txgs()` reads these records during import and repopulates `ms_unflushed_txg`, `ms_unflushed_dirty`, and `spa_metaslabs_by_flushed`.

Each per-TXG log space map stores `SM_ALLOC` and `SM_FREE` records. The records are pool-wide and include vdev information through the space map v2 double-word encoding when needed.

## In-Memory Structures

The SPA tracks metaslabs with unflushed changes in `spa_metaslabs_by_flushed`, ordered by `ms_unflushed_txg`. This ordering drives old-first flushing and determines when logs are obsolete.

`spa_sm_logs_by_txg` stores `spa_log_sm_t` nodes ordered by log TXG. Each node records the log object, TXG, open `space_map_t` during import if applicable, number of blocks, and number of metaslabs whose oldest unflushed TXG points at that log.

`spa_log_summary` aggregates log block counts, total metaslab counts, dirty metaslab counts, and TXG ranges into a short queue. The flushing heuristic uses this summary instead of walking every log node in syncing context.

Each metaslab has `ms_unflushed_allocs` and `ms_unflushed_frees`, and this file's import callback updates those trees by XOR-like remove/add behavior so repeated alloc/free transitions cancel correctly.

## Flush Policy

The file implements two main heuristics.

The memory heuristic uses `spa_log_sm_memused()` and `spa_log_exceeds_memlimit()` to compare unflushed range-tree memory against both `zfs_unflushed_max_mem_amt` and `zfs_unflushed_max_mem_ppm` of physical memory.

The block/TXG heuristic uses `spa_log_sm_set_blocklimit()`, `spa_estimate_incoming_log_blocks()`, and `spa_estimate_metaslabs_to_flush()`. The block limit is derived from dirty metaslab counts and `zfs_unflushed_log_block_pct`, clamped by `zfs_unflushed_log_block_min` and `zfs_unflushed_log_block_max`; dirty TXG depth is bounded by `zfs_unflushed_log_txg_max`. The estimator projects recent incoming log blocks into future TXGs and uses `spa_log_summary` to estimate how many dirty metaslabs must be flushed per TXG to remain below limits.

`spa_flush_metaslabs()` runs in sync pass 1, exits early when the feature is inactive or there are no tracked metaslabs, avoids dirtying final empty export TXGs unless a full flush is requested, creates the syncing log if flushing is needed, then walks `spa_metaslabs_by_flushed`. Dirty metaslabs are flushed via `metaslab_flush()` under `ms_sync_lock` and `ms_lock`; clean-but-tracked metaslabs are bumped with `metaslab_unflushed_bump()`. The loop stops when the block heuristic is satisfied and memory pressure is below limit.

## Log Lifecycle

`spa_sync_close_syncing_log_sm()` records the just-written log's block count, increments `sus_nblocks`, adds incoming blocks to the summary, verifies summary/log/metaslab counts in debug mode, closes the syncing space map, and clears an export-time flush-all request.

`spa_cleanup_old_sm_logs()` looks up the log ZAP, finds the oldest metaslab in `spa_metaslabs_by_flushed`, and frees every log whose TXG is older than that metaslab's unflushed TXG. For each destroyed log it removes the AVL node, frees the space map object, removes the ZAP key, decrements summary block counts, decrements `sus_nblocks`, and frees the `spa_log_sm_t`.

The summary update helpers are careful about corner cases from device removal, loaded metaslabs, import failure teardown, and full-pool flushes. `spa_log_summary_decrement_blkcount()` can delete whole summary rows, decrement a row, or preserve the last row when the current TXG's log shares a summary entry with older destroyed logs.

## Import Path

`spa_ld_log_spacemaps()` initializes the block limit, loads per-vdev unflushed TXGs, loads log metadata from the MOS ZAP, then enters the config lock as reader and replays log data.

`spa_ld_log_sm_metadata()` rebuilds `spa_sm_logs_by_txg` from ZAP entries and increments each log's metaslab count by walking `spa_metaslabs_by_flushed`. Missing log entries for a metaslab's unflushed TXG are treated as import failures in production and assertions in debug builds.

`spa_ld_log_sm_data()` skips replay for read-only imports. For writable imports it prefetches log dnodes and streams up to a small window of log space maps, records each log's block count and summary row, then calls `space_map_iterate()` with `spa_ld_log_sm_cb()`. The callback resolves the top-level vdev, skips removed/non-concrete vdevs, ignores entries older than the target metaslab's unflushed TXG, and applies alloc/free entries to the metaslab's unflushed trees. After replay it recalculates each tracked metaslab's allocated space, updates metaslab group space, recalculates weight, sums unflushed memory, and optionally debug-loads metaslabs.

## Tunables

The file defines module parameters for unflushed memory hard limit and ppm limit, log block min/max and percentage, dirty TXG maximum, log walking depth, summary length, minimum metaslabs to flush, and the test-only `zfs_keep_log_spacemaps_at_export`.

## Risks And Invariants

Most routines assume sync pass 1 and syncing context when mutating log structures. Summary counts, AVL log counts, AVL metaslab counts, and `sus_nblocks` must agree; `spa_log_summary_verify_counts()` enforces this under `ZFS_DEBUG_LOG_SPACEMAP`.

Correctness depends on `ms_unflushed_txg` ordering, accurate dirty metaslab counts, and replay filtering of log entries older than a metaslab's flushed state. Import must fail rather than proceed if a metaslab references a log TXG missing from the MOS log ZAP, because otherwise unflushed frees/allocs could be silently lost.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/spa_log_spacemap.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/spa_misc.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/spa_misc.c

## Role

`spa_misc.c` is the central miscellaneous support file for the Storage Pool Allocator. It defines the SPA namespace, SPA config lock implementation, pool object allocation/destruction, reference management, global spare and L2ARC-device tracking, administrative vdev locking wrappers, pool accessors, space accounting helpers, import-progress reporting, initialization/finalization ordering, scan/stat helpers, exported symbols, and many module tunables.

It is not a single algorithmic unit. Its main value is coordinating cross-subsystem invariants and providing common state-management routines used by vdev, DMU, DSL, ZIO, scan, import/export, and pool administration paths.

## Locking Model

The opening block documents the SPA locking hierarchy. `spa_namespace_lock` protects pool namespace lookup/add/remove, zero-to-nonzero refcount transitions, rename, import/export boundaries, and vdev topology operations. `spa_refcount` tracks active users. `spa_config_lock[]` is an ordered set of handoff-capable rw-style locks: `SCL_CONFIG`, `SCL_STATE`, `SCL_ALLOC`, `SCL_ZIO`, `SCL_FREE`, and `SCL_VDEV`.

`spa_config_lock_init()` and `spa_config_lock_destroy()` initialize and tear down the per-SPA lock array. `spa_config_tryenter()` tries a subset of locks and unwinds partial acquisition on conflict. `spa_config_enter_impl()` handles reader/writer acquisition, writer preference, and priority reader acquisition for MMP. `spa_config_exit()` releases in reverse lock order and broadcasts waiters. `spa_config_held()` tests reader/writer holdings.

The namespace wrapper functions provide enter, tryenter, interruptible enter, exit, wait, broadcast, and held checks. `spa_lookup()` normalizes dataset-like names to pool names and waits out concurrent import/export activity not owned by the current thread.

## SPA Lifecycle

`spa_add()` allocates and initializes a new `spa_t`: mutexes, condition variables, per-TXG free bplists, identity fields, deadman settings, allocator selection, refcount, config locks, stats, namespace AVL insertion, altroot/cachefile configuration, label feature nvlists, feature refcount cache, allocation geometry defaults, flushed metaslab/log-space-map AVL trees, log summary list, config list, load info, and leaf list.

`spa_remove()` performs the matching teardown after the pool is closed and uninitialized. It removes the SPA from the namespace, frees root/load-name/config structures, destroys allocator state, AVL/list structures, nvlists, config, refcount, stats, config locks, bplists, checksum templates, CVs, mutexes, and finally the `spa_t` itself.

`spa_init()` initializes global SPA state and dependent subsystems in a specific order, including FMA, refcounts, unique IDs, btrees, metaslab stats, BRT, DDT, ZIO, DMU, ZIL, vdev stats/math/file support, properties, checksums, features, scan, QAT, import-progress procfs, and ZAP. `spa_fini()` evicts all pools and tears these down in reverse-compatible order.

## Vdev Administration

`spa_vdev_enter()` and `spa_vdev_detach_enter()` acquire `spa_vdev_top_lock`, the namespace lock, stop autotrim, optionally stop rebuild for detach, and enter all config locks as writer through `spa_vdev_config_enter()`. The returned TXG is one past the last synced TXG.

`spa_vdev_config_exit()` reassesses DTLs, notes config changes, validates metaslab classes, exits all config locks, optionally triggers panic injection, waits for the requested TXG to sync on success, cancels initialize/trim/autotrim for a removed vdev, frees detached vdev state under state locks, and writes the cachefile when configuration changed. `spa_vdev_exit()` restarts autotrim and rebuild, calls the config exit helper, releases namespace and top-lock, and returns the operation error.

`spa_vdev_state_enter()` and `spa_vdev_state_exit()` cover state-only changes such as online/offline/fault/degrade/clear. Root pools split lock acquisition around `SCL_ZIO` so opening vdevs does not deadlock on root filesystem I/O. State exit reassesses DTLs, dirties top vdev state when needed, waits for sync for user-visible synchrony, and updates the cachefile on config change.

## Namespace, Refcounts, And Aux Devices

`spa_open_ref()`, `spa_close()`, `spa_async_close()`, and `spa_refcount_zero()` wrap SPA refcount operations with assertions appropriate to namespace locking, pool import/export, or async dataset eviction.

Hot spares and L2ARC cache devices use the shared `spa_aux_t` AVL helper functions. Spares maintain a reference count and active pool GUID because a spare can be listed in multiple pools and active in one. L2ARC devices use the same infrastructure, though cache devices currently only support one active pool. Public routines add, remove, test, and activate spare/L2ARC entries under their own global locks.

## Space And Allocation Helpers

The file defines important pool-space tunables and calculations. `spa_get_worst_case_asize()` inflates logical size by `spa_asize_inflation`, accounting for worst-case RAID-Z parity, multiple DVAs, and dittoed DDT blocks. `spa_get_slop_space()` computes reserved slop space from total pool space, `spa_slop_shift`, `spa_min_slop`, `spa_max_slop`, and embedded log classes. `spa_update_dspace()` updates raw/usable device space while reserving non-allocating vdev space and adding special/dedup/BRT accounting.

`spa_preferred_class()` chooses a metaslab class for allocation. DDT objects may use the dedup class, then special class, then normal class. Metadata and configured user indirects prefer the special class. Small blocks can use the special class only while preserving `zfs_special_class_metadata_reserve_pct` of special-class capacity for metadata.

Other helpers expose metaslab classes, DDT/special/slog presence, deflated DVA sizes, block pointer data size, and dirty data totals.

## Import Progress And Status

The import-progress section maintains a global procfs list of active imports. Entries track pool GUID, pool name, load state, notes, MMP seconds remaining, and rewind max TXG. Routines initialize/destroy the procfs list, add/remove import entries, and update state, notes, MMP check countdown, and max TXG.

`spa_load_failed()` and `spa_load_note()` format debug messages for import/load paths, with `spa_load_note()` also updating import-progress notes.

`spa_state_to_name()` returns user-facing pool state strings such as `ONLINE`, `DEGRADED`, `SUSPENDED`, `FAULTED`, `UNAVAIL`, or `TRANSITIONING`. `spa_scan_stat_init()` and `spa_scan_get_stats()` collect persistent and pass-local scrub/error-scrub stats for status reporting.

## Miscellaneous Interfaces

The file includes GUID generation and lookup, load GUID generation, `snprintf_blkptr()`, `spa_freeze()`, `zfs_panic_recover()`, a limited lowercase-hex `zfs_strtonum()`, MOS feature activation/deactivation, allocation-class feature activation, object-set eviction wait lists, pool property accessors, checkpoint helpers, multihost/hostid accessors, max block/dnode size checks, missing top-vdev tracking, and async-destroy suspension when a checkpoint plus low space could suspend the pool.

The end of the file exports many SPA symbols and defines module parameters for debug flags, recovery behavior, free-leak-on-EIO behavior, deadman settings, asize inflation, DDT/special allocation policy, slop shift, and allocator count/CPU grouping.

## Risks And Invariants

This file is heavy on cross-subsystem lock ordering. Changes to config-lock acquisition order, namespace/refcount rules, or vdev enter/exit sequencing can create deadlocks or break administrative synchrony guarantees.

Space accounting helpers feed ENOSPC decisions and allocator class routing. Errors in slop-space, non-allocating-vdev reservation, or special-class reserve calculations can expose pools to out-of-space suspension or misplace metadata. Lifecycle functions must remain aligned with `spa_t` field ownership; missing teardown or reordered subsystem finalization can leak resources or leave callbacks/kstats/procfs entries dangling.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/spa_misc.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/spa_stats.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/spa_stats.c

## Role

`spa_stats.c` implements per-pool observability for the SPA. It creates procfs rolling histories and kstats for recent reads, TXG syncs, `dmu_tx_assign()` latency, multihost protection writes/skips, pool state, pool GUID, and pool-level I/O counters.

The file is controlled by tunables for history lengths. Most history paths are cheap no-ops when the associated history length is zero and the list is empty.

## Read History

The read-history section records recent `arc_read` calls in `spa_read_history_t`: completion time, objset, object, level, block ID, origin buffer, ARC flags, PID, process name, and procfs node ID. `spa_read_history_init()` installs a per-pool `reads` procfs file with a clear callback; `spa_read_history_destroy()` uninstalls and truncates it.

`spa_read_history_add()` skips work when `zfs_read_history` is disabled, and can exclude ARC cache hits unless `zfs_read_history_hits` is enabled. On record creation it captures process identity and bookmark fields, appends to the procfs list under its lock, increments list size, and truncates to the configured maximum.

## TXG History

TXG history records one `spa_txg_history_t` per recent transaction group, including TXG number, current state, bytes/operations read and written, dirty bytes, and timestamps for TXG state transitions through committed.

`spa_txg_history_add()` starts a new TXG record at birth/open time. `spa_txg_history_set()` records a completed state timestamp and increments the stored state. `spa_txg_history_init_io()` captures vdev stats before `spa_sync()`, records the wait-for-sync timestamp, and returns a temporary `txg_stat_t`. `spa_txg_history_fini_io()` captures post-sync vdev stats, records the synced timestamp, calculates read/write byte and op deltas plus dirty bytes, stores them in the TXG history row, and frees the temporary stat object.

The procfs output shows TXG, birth time, compact state character, dirty/read/write counters, and elapsed open/quiesce/wait/sync durations.

## TX Assign Histogram

The `dmu_tx_assign` kstat is a named histogram with 42 power-of-two buckets from 1 ns up to about 2,199 seconds. `spa_tx_assign_init()` allocates and names the buckets under `zfs/<pool>/dmu_tx_assign`. `spa_tx_assign_add_nsecs()` finds the first bucket whose threshold is at least the supplied duration and atomically increments it.

`spa_tx_assign_update()` clears buckets on kstat write and trims trailing zero buckets on read by lowering `ks_ndata` and `ks_data_size`.

## MMP History

The multihost-protection history records attempted MMP writes and skipped-write spans. A `spa_mmp_history_t` stores an ID, TXG, UTC timestamp, MMP delay, vdev GUID/path/label, I/O error, error-start time, and duration.

`spa_mmp_history_add()` appends either a write record or an error/skip record. For skipped writes, `vdev_guid` is reused as a count initialized to one and `error_start` marks the beginning of the skip interval. `spa_mmp_history_set_skip()` updates the duration and increments that count for a matching skip record. `spa_mmp_history_set()` fills in completion error and duration for an issued MMP write.

The procfs output uses a different formatting path for skip records versus normal write records.

## State, GUID, And I/O Kstats

`spa_state_init()` creates a raw no-header kstat named `zfs/<pool>/state` that reports `spa_state_to_name(spa)`. It is intentionally lockless so monitoring can read it as a lightweight heartbeat without invoking `zpool` paths.

`spa_guid_init()` creates a raw no-header kstat named `zfs/<pool>/guid` that reports `spa_guid(spa)`.

The `iostats` named kstat contains counters for manual trim, autotrim, simple trim, ARC reads/writes, and direct reads/writes. `spa_iostats_trim_add()`, `spa_iostats_read_add()`, and `spa_iostats_write_add()` atomically add values to the appropriate counters. A write to the kstat resets the data to `spa_iostats_template`.

## Lifecycle

`spa_stats_init()` initializes read history, TXG history, TX assign histogram, MMP history, state kstat, GUID kstat, and I/O stats for a newly added SPA. `spa_stats_destroy()` tears down I/O stats, state, TX assign histogram, TXG history, read history, MMP history, and GUID.

The file exposes module parameters for read history length, inclusion of read hits, TXG history length, and multihost history length.

## Risks And Invariants

History list operations must hold the procfs list lock while appending, truncating, clearing, or searching. Kstat update paths must preserve the allocated backing data lifetime until deletion.

Most counters are diagnostic, not correctness-critical, but TXG history is used by `txg.c` around state transitions and `spa_sync()` I/O measurement. Missing or reordered calls can make `/proc` output misleading, especially for diagnosing sync latency and pool import or MMP behavior.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/spa_stats.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/space_map.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/space_map.c

## Role

`space_map.c` implements OpenZFS's on-disk space map object format and core operations for reading, writing, loading, estimating, truncating, allocating, and freeing space maps. A space map is an append-only log of allocation or free extents. Higher-level code uses it for metaslab space maps, DTLs, and log space maps.

The file understands the legacy single-word encoding, space map v2 double-word encoding, and debug entries that record TXG/sync-pass context or pad blocks.

## Entry Decoding And Iteration

`sm_entry_is_debug()`, `sm_entry_is_single_word()`, and `sm_entry_is_double_word()` classify raw 64-bit words by prefix.

`space_map_iterate()` streams through the first `end` bytes of a space map object. It prefetches the stream, holds each DMU buffer, walks 64-bit words, updates current TXG and sync-pass on debug entries, decodes single-word or double-word entries, reconstructs shifted absolute offsets and runs, validates alignment and bounds against `sm_start`, `sm_size`, and `sm_shift`, then calls the supplied callback with a `space_map_entry_t`.

Double-word entries store run and vdev in the first word and type/offset in the second word. Single-word entries have no vdev ID and use `SM_NO_VDEVID`.

## Incremental Destruction

`space_map_incremental_destroy()` destructively deletes entries from the end of a space map while invoking a callback for each logical entry. It cannot simply scan backwards because the second word of a double-word entry is not self-identifying, so `space_map_reversed_last_block_entries()` reads the final block and builds a reverse-order buffer while preserving double-word pairs.

For each reversed entry, the function invokes the callback, updates `smp_alloc` in the opposite direction of the destroyed record, and subtracts one or two words from `smp_length`. Debug entries only reduce length. When the map reaches length zero, allocated space must also be zero.

Callers are responsible for holding the correct higher-level locks because this path mutates the map.

## Loading Into Range Trees

`space_map_load_length()` and `space_map_load()` replay a space map into a `zfs_range_tree_t`. When loading `SM_FREE`, the target range tree is first populated with the entire map range. During iteration, entries matching the requested map type add ranges and opposite entries remove ranges. On read error the target tree is vacated.

`space_map_load_callback()` verifies that adding a segment will not exceed the map size before adding it.

## Histograms

The file supports optional on-disk histograms stored in `space_map_phys_t`. `space_map_histogram_clear()` clears the histogram only when the bonus buffer has the modern physical size. `space_map_histogram_verify()` ensures the in-core range tree has no ranges below the space map allocation shift. `space_map_histogram_add()` transfers range-tree histogram buckets into the space map's 32 buckets, normalizing ranges larger than the representable bucket range into the last bucket.

Histogram feature reference counts are managed when allocating and freeing space map objects if `SPA_FEATURE_SPACEMAP_HISTOGRAM` is enabled and the object's bonus size uses the modern format.

## Writing

`space_map_write()` is the public write path. It requires syncing context, dirties the bonus buffer, keeps `smp_object` updated for compatibility, returns early for empty trees, updates `smp_alloc` according to `SM_ALLOC` or `SM_FREE`, records initial range-tree node/space counts, calls `space_map_write_impl()`, then verifies the range tree was not changed while writing.

`space_map_write_impl()` writes an intro debug entry, estimates final size in debug builds, holds the last data block at the append offset, then walks the range tree. It chooses double-word entries only when `SPA_FEATURE_SPACEMAP_V2` is active and offset/run/vdev requirements exceed single-word capacity, a vdev ID is present, or the testing tunable forces occasional double-word entries.

`space_map_write_seg()` performs the actual append. It splits long segments by the maximum representable run, advances blocks as needed, and pads a one-word remainder at the end of a block with an empty debug entry so a two-word entry is never split across blocks. It updates `smp_length` as words are written.

## Object Lifecycle

`space_map_open()` allocates an in-core `space_map_t`, stores geometry and object fields, holds the DMU bonus buffer, discovers the data block size, and returns the opened map. `space_map_close()` releases the bonus buffer and frees the in-core object.

`space_map_truncate()` either frees/reallocates the object if the bonus size or block sizes are outdated, or frees all data ranges in place. It clears the histogram, dirties the bonus buffer, and resets `smp_length` and `smp_alloc`.

`space_map_alloc()` allocates a DMU object with `DMU_OT_SPACE_MAP` data and `DMU_OT_SPACE_MAP_HEADER` bonus data, using the configured indirect block shift `space_map_ibs`. `space_map_free_obj()` decrements the histogram feature count when appropriate and frees the object. `space_map_free()` wraps object free and clears the in-core object ID.

## Estimation And Accessors

`space_map_estimate_optimal_size()` computes a worst-case byte estimate for writing a range tree to a space map. It uses range-tree histograms rather than walking every segment, accounts for single-word versus double-word encodability, feature state, forced double-word testing, split entries for very large ranges, and worst-case debug padding.

`space_map_object()`, `space_map_allocated()`, `space_map_length()`, and `space_map_nblocks()` expose object ID, allocated bytes, logical encoded length, and number of data blocks.

## Risks And Invariants

Encoding and decoding must agree exactly across single-word, double-word, and debug entries. A double-word entry may not cross a data-block boundary, which is why padding debug entries exist.

All offsets and lengths are stored shifted by `sm_shift`; callers must provide aligned ranges within `[sm_start, sm_start + sm_size)`. Write paths assume syncing context and no concurrent mutation of the source range tree. Truncation and incremental destruction modify on-disk metadata and require caller-side synchronization.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/space_map.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/space_reftree.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/space_reftree.c

## Role

`space_reftree.c` implements space reference trees, a small helper abstraction for combining range trees with reference counts. A normal range tree represents membership as present or absent. A reference tree records signed reference-count deltas at segment boundaries, making unions and intersections of multiple maps easy to derive.

The main documented consumer is `vdev_dtl_reassess()`, which computes missing/outage regions for interior vdevs. For example, RAID-Z outage regions are where the reference count reaches parity plus one, while mirror outage regions are where all children are missing.

## Data Structure

The tree is an AVL tree of `space_ref_t` records ordered by `sr_offset`, with pointer comparison as a tie breaker. Tie-breaking allows multiple delta records at the same offset rather than coalescing them during insertion.

Each segment contributes two nodes: a positive reference-count delta at the start and a negative delta at the end. A running sum over the ordered tree yields the active reference count for every interval.

## API

`space_reftree_create()` initializes an AVL tree with the local comparator and `space_ref_t` layout. `space_reftree_destroy()` destroys all nodes with `avl_destroy_nodes()` and frees each `space_ref_t` before destroying the tree.

`space_reftree_add_seg()` adds one segment by inserting start and end delta nodes. `space_reftree_add_map()` walks a `zfs_range_tree_t` and adds every range segment with the supplied signed reference count.

`space_reftree_generate_map()` converts the reference tree back into a normal range tree. It vacates the output tree, walks delta nodes in order, maintains a running `refcnt`, opens an output range when `refcnt >= minref`, closes it when the count falls below `minref`, and adds non-empty intervals to the output range tree.

## Risks And Invariants

The sum of all deltas must return to zero by the end of generation, and no output interval may remain open. `space_reftree_generate_map()` asserts both conditions.

Because duplicate offsets are allowed through pointer tie-breaking, correctness depends on processing all same-offset deltas before interpreting the next nonzero-length interval. Zero-length output intervals are skipped. Consumers should treat the tree as a temporary computation structure and destroy it after generating the desired map.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/space_reftree.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/txg.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/txg.c

## Role

`txg.c` implements ZFS transaction group coordination. Transaction groups batch in-memory mutations into monotonically increasing TXG IDs, move them through open, quiescing, and syncing states, and provide wait/kick/delay/list APIs used by DMU, DSL, SPA, ZIL, and administrative sync tasks.

The file owns the two worker threads that advance TXGs: a quiesce thread and a sync thread. It also implements per-TXG callback dispatch and generic per-TXG object lists.

## TXG States

The file's top comment explains the three active TXG states.

The open TXG accepts new transactions. A TXG exits open state when thresholds, timeouts, sync waiters, scans, or administrative work require it to move forward.

The quiescing TXG no longer accepts new transactions but waits for all open handles to be released to sync. This gives in-memory operations time to finish before disk sync.

The syncing TXG writes accumulated dirty state to stable storage through `spa_sync()`, potentially in multiple sync passes until metadata changes converge and a new uberblock can be written.

## Initialization And Threads

`txg_init()` clears `tx_state_t`, allocates per-CPU `tx_cpu_t` state, initializes per-CPU locks, open locks, per-TXG condition variables and callback lists, initializes sync-lock CVs, and sets the initial open TXG.

`txg_sync_start()` starts the quiesce and sync threads and sets `tx_threads` to two. `txg_sync_stop()` waits far enough ahead to drain deferred metaslab work, sets `tx_exiting`, wakes all TXG CVs, and waits for both threads to exit. `txg_fini()` asserts threads are stopped, destroys locks/CVs/lists/taskq, frees per-CPU state, and clears the structure.

`txg_thread_enter()`, `txg_thread_wait()`, and `txg_thread_exit()` wrap thread lock/CPR integration, idle waits, exit bookkeeping, and `thread_exit()`.

## Open Handles And Quiescing

`txg_hold_open()` chooses a per-CPU slot with `CPU_SEQID_UNSTABLE`, takes that slot's `tc_open_lock`, reads the current open TXG, increments the per-TXG per-CPU hold count under `tc_lock`, and returns a `txg_handle_t`. Holding `tc_open_lock` prevents that TXG from being fully closed to new entrants until the caller releases to quiesce.

`txg_rele_to_quiesce()` releases the open lock. `txg_rele_to_sync()` decrements the per-CPU hold count and broadcasts the per-TXG CV when it reaches zero. `txg_register_callbacks()` moves DMU transaction commit callbacks onto the per-CPU callback list for the handle's TXG.

`txg_quiesce()` takes every per-CPU open lock to block new entrants, increments `tx_open_txg`, records open/quiesce timestamps in SPA TXG history, releases open locks so new transactions enter the next TXG, then waits for all per-CPU hold counts for the old TXG to drop to zero. It then records the quiesced timestamp.

## Sync And Quiesce Threads

`txg_quiesce_thread()` waits until a future TXG has been requested for quiescing and there is no already-quiesced TXG waiting for sync. It sets `tx_quiescing_txg`, drops `tx_sync_lock`, calls `txg_quiesce()`, reacquires the lock, hands the TXG to the sync thread via `tx_quiesced_txg`, and broadcasts sync/quiesce CVs.

`txg_sync_thread()` wakes when scanning is active, a sync waiter exists, a quiesced TXG is ready, or `zfs_txg_timeout` expires. It skips syncing while the pool is suspended, requests quiescing when needed, consumes `tx_quiesced_txg`, sets `tx_syncing_txg`, drops the lock, records initial I/O stats through `spa_txg_history_init_io()`, calls `spa_sync(spa, txg)`, records final I/O stats, marks `tx_synced_txg`, clears `tx_syncing_txg`, broadcasts sync waiters, and dispatches commit callbacks.

`txg_dispatch_callbacks()` lazily creates a `tx_commit_cb` taskq, moves registered callbacks into temporary lists, and dispatches them to worker threads. `txg_wait_callbacks()` waits for outstanding callback tasks and warns in comments that calling from a callback would deadlock.

## Waiting, Kicking, And Delay

`txg_wait_synced_flags()` waits until a target TXG has synced, defaulting TXG zero to open plus deferred size. It records the highest requested sync TXG, broadcasts the sync thread, and waits either interruptibly, uninterruptibly, or with early `ESHUTDOWN` return when `TXG_WAIT_SUSPEND` is requested and the pool is suspended. `txg_wait_synced()` wraps it with no flags.

`txg_wait_open()` waits until the open TXG reaches a target, optionally marking that target for immediate quiescing. It accounts wait time as I/O wait for callers that request quiescing and idle wait otherwise.

`txg_kick()` asks the sync thread to advance at least through a supplied TXG. `txg_wait_kick()` broadcasts sync-done waiters. `txg_delay()` sleeps a caller for a requested time when its TXG is still open and the pipeline is backed up, aborting if the TXG advances or the pipeline stalls.

`txg_stalled()` reports that quiescing is waiting beyond the open TXG. `txg_sync_waiting()` reports whether syncing is at or behind a requested TXG or a quiesced TXG is waiting.

## Per-TXG Lists

The bottom section implements `txg_list_t`, an intrusive list set indexed by `txg & TXG_MASK`. `txg_list_create()` initializes the lock, offset, SPA pointer, and heads. `txg_list_add()` inserts at the head if not already present for the TXG; `txg_list_add_tail()` inserts at the tail. `txg_list_remove()` removes the head, and `txg_list_remove_this()` removes a specific object. `txg_list_member()`, `txg_list_head()`, `txg_list_next()`, `txg_list_empty()`, `txg_all_lists_empty()`, and `txg_list_destroy()` provide membership, traversal, emptiness, and teardown helpers.

In debug builds, `txg_verify()` ensures manipulated TXGs are active: not older than synced state, not beyond the open TXG, and within the concurrent TXG window.

## Tunables And Exports

`zfs_txg_timeout` defaults to five seconds and controls the maximum time worth of delta per TXG before the sync thread advances work. The file exports TXG lifecycle, hold/release, callback, delay, wait, stalled, and sync-waiting functions, and exposes `zfs_txg_timeout` as a module parameter.

## Risks And Invariants

The ordering around `tc_open_lock`, per-CPU hold counts, `tx_sync_lock`, and CV broadcasts is the core correctness constraint. A TXG cannot be handed to sync until every open handle has released to sync, and new handles must observe monotonically nondecreasing open TXGs.

The sync and quiesce threads maintain a bounded pipeline: one open TXG, at most one quiescing TXG, and at most one quiesced TXG waiting for sync. Waiters must not hold DSL pool config locks when calling the wait APIs, as asserted in the code. Callback dispatch occurs only after the TXG has synced; callback list ownership is transferred to taskq-owned temporary lists.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/txg.c -->