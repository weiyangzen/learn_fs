# sources/distributed-fs/ceph-client/fs/f2fs/shrinker.c

## Purpose
`shrinker.c` implements F2FS memory-reclaim integration. It registers mounted F2FS instances in a global list and provides count/scan helpers that reclaim extent-cache entries, clean NAT cache entries, excess free NIDs, and explicit donated page-cache ranges from files that have completed a donate workflow.

## Important APIs, types, and functions
Global state consists of `f2fs_list`, `f2fs_list_lock`, and `shrinker_run_no`. `f2fs_list` links every mounted `struct f2fs_sb_info` through `sbi->s_list`; `shrinker_run_no` prevents a single scan from looping indefinitely after moving scanned entries to the tail.

The reclaim count helpers are `__count_nat_entries`, `__count_free_nids`, and `__count_extent_cache`. Public shrinker entry points are `f2fs_shrink_count` and `f2fs_shrink_scan`. Additional cache-donation APIs are `f2fs_donate_files`, `f2fs_reclaim_caches`, and the internal `do_reclaim_caches`. Mount lifecycle integration uses `f2fs_join_shrinker` and `f2fs_leave_shrinker`.

## Control flow
`f2fs_shrink_count` walks the global mount list under `f2fs_list_lock`. For each instance it tries `sbi->umount_mutex`; if unmount is active it skips that instance. Once locked, it drops the global spinlock, adds reclaimable read extent cache entries, block-age extent cache entries, clean NAT entries, and excess free-NID entries, then reacquires the list lock and releases `umount_mutex`.

`f2fs_shrink_scan` similarly walks the list, but first increments `shrinker_run_no` and stamps each scanned `sbi`. For each instance it reclaims a quarter of the requested objects from block-age extents and a quarter from read extents, then uses the remaining budget for clean NATs and free NIDs. After scanning an instance, it moves that instance to the tail so future scans are fair across mounts. The scan stops when the requested budget is met, the list wraps to an already-stamped instance, or the list ends.

`f2fs_donate_files` sums `sbi->donate_files` across mounted instances while using the same list and unmount locking pattern. `f2fs_reclaim_caches` spends a kilobyte budget across instances by calling `do_reclaim_caches`. That helper converts the budget to pages, rotates through `DONATE_INODE` entries under `sbi->inode_lock[DONATE_INODE]`, grabs each inode with `igrab`, locks it, invalidates the donated page range with `invalidate_inode_pages2_range`, marks `FI_DONATE_FINISHED`, drops the inode, and reschedules as needed.

`f2fs_leave_shrinker` is the unmount-side cleanup path. It explicitly shrinks all remaining read and block-age extent cache entries for that instance, then removes the `sbi` from the global list under the spinlock.

## State and persistence behavior
All state is runtime-only. The global list is rebuilt by mounted filesystems and does not persist. Shrinker counts derive from in-memory extent-tree counters, NAT counters, and free-NID counters. Donated cache reclamation only invalidates page-cache ranges and sets an in-memory inode flag; it does not directly alter on-disk metadata.

The important lifetime guard is `sbi->umount_mutex`, used by count, scan, donation count, and reclaim flows to avoid racing with `f2fs_put_super`. The global spinlock protects list topology and scan ordering but is deliberately dropped before doing potentially blocking reclaim work.

## Dependencies and integration points
This file depends on F2FS node-manager state (`NM_I`, NAT counters, free-NID counters), extent-cache state (`sbi->extent_tree[EX_READ]` and `[EX_BLOCK_AGE]`), reclaim functions `f2fs_shrink_read_extent_tree`, `f2fs_shrink_age_extent_tree`, `f2fs_try_to_free_nats`, and `f2fs_try_to_free_nids`, inode donation lists, VFS inode/page-cache APIs, and kernel shrinker callback conventions.

It integrates with mount/unmount through `f2fs_join_shrinker` and `f2fs_leave_shrinker`, with system memory pressure through the shrinker count/scan callbacks, and with the donation mechanism through `sbi->donate_files`, `DONATE_INODE`, `gdonate_list`, `donate_start`, `donate_end`, and `FI_DONATE_FINISHED`.

## Risks
The primary risk is lifetime and lock ordering. The code must not hold `f2fs_list_lock` while invalidating page cache or shrinking trees, and it must not touch an `sbi` being torn down. The `mutex_trylock` skip behavior avoids blocking unmount but can make reclaim less aggressive for busy filesystems.

Fairness depends on `shrinker_run_no` and `list_move_tail`. If run numbers wrap to zero incorrectly or list movement changes while scanning, one instance could be over-scanned or skipped. The code avoids zero run numbers, but changes to list handling should preserve the wrap detection.

Budget semantics are approximate. Extent reclaim receives fixed quarter-budgets before NAT/free-NID reclaim, so the returned freed count may be below `nr_to_scan` even when other cache classes could free more. `do_reclaim_caches` returns the remaining kilobyte budget, not the amount freed, so callers must preserve that convention.

Donation reclaim risk includes invalidating the wrong page-cache range, racing inode eviction after list selection, and repeatedly walking files already marked `FI_DONATE_FINISHED`. `igrab`, inode locking, list rotation, and the finished flag reduce those risks.

## Test signals
Shrinker tests should mount multiple F2FS instances and verify count aggregation, scan fairness, list tail rotation, and unmount skip behavior. Reclaim signals include extent-cache-only pressure, NAT-only pressure, free-NID counts below and above `MAX_FREE_NIDS`, and mixed cache budgets where freed count reaches or misses `nr_to_scan`.

Donation tests should cover empty donate lists, inode eviction causing `igrab` failure, repeated calls after `FI_DONATE_FINISHED`, ranges spanning many pages, partial kilobyte budgets, and concurrent unmount. Unmount tests should confirm `f2fs_leave_shrinker` drains extent caches and removes the instance from future count/scan walks.
