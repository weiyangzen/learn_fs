# Group Research: group_751_linux_sources_os_linux_linux_fs_f2fs_segment_c_sources_os_linux_linu_0d452ee91db6

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/segment.c -->
# File Research: sources/os/linux/linux/fs/f2fs/segment.c

Read completely: 5928 lines.

## Purpose
Implements the F2FS segment manager: current segment allocation, SIT validity tracking, dirty/pre-free segment accounting, discard/TRIM scheduling, summary block persistence, flush merging, atomic-write block replacement, block write placement, zoned-device write-pointer handling, and segment-manager lifecycle.

## Main Responsibilities
- Chooses when to use SSR versus LFS allocation and allocates new current segments/sections.
- Maintains SIT entries, valid-block bitmaps, checkpoint-valid bitmaps, discard maps, section counters, and segment mtimes.
- Tracks dirty, pre-free, victim, and pinned sections for GC and checkpoint.
- Queues, merges, issues, waits for, drops, and times out discard commands, including zone reset commands on zoned devices.
- Writes and restores compact/normal current-segment summary blocks and NAT/SIT journals.
- Coordinates metadata/data/node write placement and block replacement for recovery, GC, and atomic writes.
- Builds and destroys all segment-manager in-memory state and slab caches.

## Key Flows
- Atomic writes: `f2fs_commit_atomic_write()` flushes file data, locks GC/write operation state, walks the COW inode, replaces original file blocks via `__replace_atomic_write_block()`, and records a revoke list so failed commits can restore old addresses.
- Filesystem balancing: `f2fs_balance_fs()` and `f2fs_balance_fs_bg()` trigger foreground/background GC, checkpointing, NAT/free-NID cleanup, and extent-cache shrinkage when free sections, dirty metadata, cached NATs, prefree segments, or roll-forward space cross thresholds.
- Flush handling: `f2fs_issue_flush()` either submits directly or merges concurrent flushes through `issue_flush_thread()` and `flush_cmd_control`, with per-device flushing for multi-device filesystems.
- Dirty segment tracking: `locate_dirty_segment()`, `f2fs_dirty_to_prefree()`, and helpers move segments among `DIRTY`, type-specific dirty maps, and `PRE` based on current and checkpoint-valid blocks.
- Discard management: discard ranges are represented as `discard_cmd` nodes in an rb-tree plus size-bucket pending lists. `__update_discard_tree_range()` merges adjacent ranges; `__submit_discard_cmd()` splits requests by device limits; wait paths use command completions and refcounts.
- Checkpoint/TRIM: `f2fs_flush_sit_entries()` writes dirty SIT entries either into the SIT journal or next SIT blocks, gathers discard candidates, and converts pre-free segments to free segments after checkpoint.
- Allocation: `get_new_segment()`, `new_curseg()`, `change_curseg()`, `get_ssr_segment()`, and `need_new_seg()` choose free or reusable segments while respecting active log type, section/zone placement, checkpoint-disabled mode, pinned sections, and ATGC.
- Write placement: `f2fs_allocate_data_block()` updates summaries, SIT maps, mtimes, dirty maps, current-segment offsets, device dirty state, and writeback queues for out-of-place writes. `f2fs_inplace_write_data()` handles IPU writes after validating segment type.
- Recovery/replacement: `f2fs_do_replace_block()` temporarily switches a curseg to the target segment, updates summary/SIT state, optionally restores the old curseg, and is used by recovery and atomic-write paths.
- Mount/build: `f2fs_build_segment_manager()` initializes flush/discard controls, SIT info, free maps, current segments, SIT entries, dirty maps, current-segment sanity checks, and GC mtime bounds.
- Zoned devices: zone reset commands replace discard for sequential zones; mount-time checks can allocate new current sections, reset empty zones, finish or zero inconsistent zones, and verify write pointers.

## Concurrency and State
- `SIT_I(sbi)->sentry_lock` protects SIT cache, valid maps, dirty SIT accounting, and checkpoint-valid counters.
- `DIRTY_I(sbi)->seglist_lock` protects dirty/pre-free/victim/pinned segment maps.
- `FREE_I(sbi)->segmap_lock` protects free segment/section maps and counters.
- Each `curseg_info` has `curseg_mutex`; `SM_I(sbi)->curseg_lock` serializes broader current-segment changes.
- Discard commands use `dcc->cmd_lock`, per-command spinlocks, completions, rb-tree/list membership, `bio_ref`, and `ref` to coordinate submit/endio/wait/removal.
- Several paths deliberately run under checkpoint, GC, or operation locks supplied by callers.

## Important Edge Cases
- F2FS bitmap bit order is reversed within bytes, so the file implements custom reverse bit search helpers for SIT/discard maps.
- Checkpoint-disabled mode tracks unusable blocks and may force SSR or reject disabling checkpoint again when unusable/free-section limits are exceeded.
- `NULL_ADDR`, `NEW_ADDR`, and `COMPRESS_ADDR` are treated specially during invalidation and allocation.
- Discard submission is skipped on corruption, unsupported devices, or io-aware busy periods; umount discard has timeout/drop behavior.
- Segment allocation failures stop checkpoint with specific reasons in non-pinning paths.
- Zoned writes require section/zone alignment; unaligned zone reset attempts return errors.
- SIT and curseg sanity checks mark corruption and require fsck on inconsistent block counts, segment types, journals, or current-segment offsets.

## Research Notes
This is the central implementation of F2FS space management. Correctness depends on tight coupling among SIT maps, free maps, dirty maps, current summaries, checkpoint state, discard state, and GC victim selection. Small changes here can affect mount recovery, fsync durability, fstrim behavior, multi-device flushing, zoned-device safety, and ENOSPC behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/segment.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/segment.h -->
# File Research: sources/os/linux/linux/fs/f2fs/segment.h

Read completely: 1052 lines.

## Purpose
Defines the F2FS segment-manager data model, address/segment conversion macros, allocation/GC mode constants, dirty-segment types, SIT/free/dirty/curseg structures, and inline helpers used by `segment.c`, GC, checkpoint, data writeback, and node management.

## Main Responsibilities
- Converts among block addresses, logical/relative segment numbers, sections, zones, SIT blocks, and summary blocks.
- Defines LFS, SSR, AT_SSR, GC, foreground/background GC, and dirty segment classifications.
- Describes in-memory SIT state through `seg_entry`, `sec_entry`, `sit_info`, and `sit_entry_set`.
- Describes segment allocation state through `free_segmap_info`, `dirty_seglist_info`, and `curseg_info`.
- Provides fast inline accessors for current segments, valid block counts, free/dirty/pre-free counts, overprovisioning, utilization, and checkpoint readiness.
- Provides SIT serialization/deserialization helpers and SIT block address flipping.
- Encodes IPU policy flags and helpers.
- Provides writeback sizing hints and discard-thread wakeup logic.

## Key Definitions
- Address macros: `MAIN_BLKADDR`, `SEG0_BLKADDR`, `START_BLOCK`, `NEXT_FREE_BLKADDR`, `GET_SEGNO`, `GET_SEC_FROM_SEG`, `GET_ZONE_FROM_SEG`, `GET_SUM_BLOCK`, and `SUM_BLK_PAGE_ADDR`.
- Capacity macros: `CAP_BLKS_PER_SEC` and `CAP_SEGS_PER_SEC` account for zoned-device unusable zone capacity.
- `victim_sel_policy` carries GC/SSR selection inputs such as dirty bitmap, search bounds, min cost, age, and age threshold.
- `seg_entry` stores segment type, valid counts, current/checkpoint valid maps, optional mirror map, discard map, and modification time.
- `sit_info` stores SIT block addresses, bitmaps, dirty SIT tracking, segment/section entry arrays, and mtime bounds for cost-benefit GC.
- `free_segmap_info` tracks free segments/sections and their bitmaps.
- `dirty_seglist_info` tracks type-specific dirty maps, generic dirty/pre-free maps, dirty section map, victim map, and pinned section map.
- `curseg_info` tracks active log state: summary block, journal, allocation type, segment type, current segment, next block offset, zone, pending next segment, and fragmentation mode state.

## Key Inline Behavior
- `get_valid_blocks()` and `get_ckpt_valid_blocks()` return segment-level or section-level counts depending on large-section mode.
- `set_ckpt_valid_blocks()` and `sanity_check_valid_blocks()` synchronize/check section checkpoint-valid counters from segment entries.
- `seg_info_from_raw_sit()`, `seg_info_to_raw_sit()`, and `seg_info_to_sit_folio()` translate between raw on-disk SIT entries and in-memory entries.
- `__set_free()`, `__set_inuse()`, `__set_test_and_free()`, and `__set_test_and_inuse()` update free segment and free section maps with counter maintenance.
- `__get_secs_required()`, `has_not_enough_free_secs()`, and `f2fs_is_checkpoint_ready()` estimate free-section requirements from dirty node/dentry/imeta/data pages and reserved sections.
- `check_block_count()` validates raw SIT valid-block count against the valid bitmap and usable segment capacity, marking the filesystem for fsck on mismatch.
- `current_sit_addr()`, `next_sit_addr()`, and `set_to_next_sit()` implement SIT double-buffering.
- `get_mtime()` computes filesystem-relative elapsed time for GC aging.
- `nr_pages_to_skip()` and `nr_pages_to_write()` bias writeback toward segment-sized or bio-sized batching.
- `wake_up_discard_thread()` wakes the discard thread only when pending requests meet granularity or a force wake is requested.

## Concurrency and Assumptions
Many helpers directly mutate shared counters and bitmaps and assume callers hold the documented locks from `segment.c`: free segmap spinlock, dirty seglist mutex, SIT sentry rwsem, current-segment locks, or checkpoint/GC locks. The header prioritizes fast inline operations over defensive locking.

## Important Edge Cases
- `GET_SEGNO()` returns `NULL_SEGNO` for invalid/non-data block addresses.
- Zoned-device capacity can make part of a segment unusable, so valid-block checks use `f2fs_usable_blks_in_seg()`.
- Free section accounting excludes current sections in some in-memory log transitions.
- Active log count changes how dentry/data dirty-page requirements are separated.
- SIT bitmap mirror checks are enabled under `CONFIG_F2FS_CHECK_FS`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/segment.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/shrinker.c -->
# File Research: sources/os/linux/linux/fs/f2fs/shrinker.c

Read completely: 246 lines.

## Purpose
Implements F2FS shrinker integration and explicit cache reclamation across mounted F2FS instances.

## Main Responsibilities
- Maintains a global list of F2FS superblocks participating in shrinker scans.
- Counts reclaimable read extent cache, block-age extent cache, clean NAT entries, and excess free NID entries.
- Reclaims those caches when the kernel shrinker asks F2FS to scan.
- Tracks and reclaims donated inode page-cache ranges for explicit cache donation/reclaim flows.
- Adds/removes filesystems from the shrinker list at mount/unmount lifecycle boundaries.

## Key Functions
- `__count_nat_entries()` returns reclaimable clean NAT cache entries.
- `__count_free_nids()` returns free-NID cache entries above `MAX_FREE_NIDS`.
- `__count_extent_cache()` sums zombie extent trees and extent nodes for a given extent type.
- `f2fs_shrink_count()` walks all mounted F2FS instances and returns total reclaimable objects or `SHRINK_EMPTY`.
- `f2fs_shrink_scan()` assigns a nonzero run id, walks the global list, shrinks age extents, read extents, NATs, and free NIDs, then rotates scanned filesystems to the tail for fairness.
- `f2fs_donate_files()` totals per-filesystem donated-file counts.
- `do_reclaim_caches()` iterates donated inodes, invalidates the configured page-cache range, and marks `FI_DONATE_FINISHED`.
- `f2fs_reclaim_caches()` applies donated-cache reclamation across mounted filesystems until the requested kilobyte budget is exhausted.
- `f2fs_join_shrinker()` and `f2fs_leave_shrinker()` manage global shrinker list membership; leave also drains extent caches for that filesystem.

## Concurrency and State
- `f2fs_list_lock` protects the global `f2fs_list` and list traversal.
- Each filesystem’s `umount_mutex` is acquired with `mutex_trylock()` to avoid racing `f2fs_put_super()`; locked filesystems are skipped rather than blocking.
- `shrinker_run_no` prevents revisiting the same filesystem during one shrink scan after list rotation.
- Donated inode lists use `sbi->inode_lock[DONATE_INODE]`; inodes are pinned with `igrab()`, locked with `inode_lock()`, then released with `iput()`.

## Important Edge Cases
- Shrinker counting/scanning skips filesystems currently unmounting.
- `shrinker_run_no` intentionally skips zero by incrementing until nonzero.
- Reclaim budget is split initially between age/read extent shrinking with `nr >> 2`, then remaining budget is used for NAT and free-NID caches.
- Donated-cache reclaim converts kilobytes to pages and returns the unreclaimed kilobyte budget.
- If an inode cannot be grabbed, reclaim continues with the next donated inode.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/shrinker.c -->