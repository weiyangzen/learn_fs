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
