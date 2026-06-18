<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/gc.h -->
# sources/distributed-fs/ceph-client/fs/f2fs/gc.h

## Purpose

`gc.h` defines garbage-collection constants, thresholds, lightweight data structures, and inline predicates used by F2FS GC and free-space pressure logic. It is included by GC callers and exposes the sleep-tuning and free-space heuristics that govern background GC behavior, zoned-device behavior, age-threshold GC, pinned-file failure limits, and victim search scale.

## Important APIs, Types, and Functions

- Sleep constants include normal and zoned minimum, maximum, urgent, and no-GC wait times.
- ATGC constants define age threshold, candidate ratio, maximum candidate count, age weight, valid-block threshold for one-time GC, and accuracy class.
- Space-pressure constants include invalid-block and free-block percentage limits, zoned no-GC and boost-GC thresholds, migration window granularity, boost multiplier, pinned-section count, pinned-file failure limits, maximum victim search, and checkpoint reserve sections.
- `struct f2fs_gc_kthread` stores the GC task, waitqueues, sleep times, wake flag, GC_MERGE foreground waitqueue, zoned thresholds, one-time valid threshold, and boost policy.
- `struct gc_inode_list` stores inodes pinned during GC in both list and radix-tree form to avoid duplicate `iget()` references.
- `struct victim_entry` represents ATGC candidates in an rb-tree and linked list, keyed by section mtime and segment number.
- `free_segs_blk_count_zoned()` sums usable blocks for free segments on zoned devices where zone capacity may be smaller than zone size.
- `free_segs_blk_count()`, `free_user_blocks()`, `limit_invalid_user_blocks()`, and `limit_free_user_blocks()` derive reclaimable user-space pressure metrics.
- `increase_sleep_time()` and `decrease_sleep_time()` adjust daemon wait time within configured bounds.
- `has_enough_free_blocks()`, `has_enough_invalid_blocks()`, and `need_to_boost_gc()` implement the high-level pressure predicates used by `gc.c`.

## Control Flow and State Behavior

The inline functions are intentionally simple and lock only where needed. Zoned free-block counting walks the free segment bitmap under `free_i->segmap_lock` and uses `f2fs_usable_blks_in_seg()` to avoid counting unusable blocks that span past zone capacity. Non-zoned free blocks are calculated from free segments. User-free blocks subtract overprovisioned blocks and clamp at zero.

Sleep time grows by the minimum sleep interval up to the maximum, unless the thread is already in no-GC sleep. Sleep time shrinks by the minimum interval down to the minimum, with a transition from no-GC sleep back to maximum sleep first. The boost predicate differs by device type: zoned devices boost when free sections fall below `boost_zoned_gc_percent`, while conventional devices boost when invalid blocks are high and free user blocks are low.

## Persistence, Locking, and Integration Points

This header does not persist state by itself, but its structures live in `struct f2fs_sb_info` and are mutated by `gc.c`, mount-option setup, sysfs tuning, and filesystem lifecycle code. Its calculations depend on `FREE_I(sbi)`, `MAIN_SEGS`, `free_segments()`, `free_sections()`, overprovisioning, `written_block_count()`, and zoned-usable-block helpers.

## Risks and Edge Cases

The key risk is pressure miscalculation: overcounting free blocks on zoned media can delay GC until allocation fails, while overly aggressive thresholds can increase write amplification. `free_user_blocks()` explicitly handles overprovisioned space exceeding free blocks. Percentage arithmetic uses `long`/`block_t` style calculations, so tests around very large devices and unusual zone capacities are useful.

## Test Signals

Tests should cover conventional and zoned free-block accounting, no-GC and boost thresholds, invalid-block pressure triggering, sleep-time boundary behavior, sysfs/mount tuning of GC thread fields, large device counts, and zone-capacity values not aligned to segment size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/gc.h -->
