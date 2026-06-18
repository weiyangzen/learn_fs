# sources/distributed-fs/ceph-client/fs/ubifs/shrinker.c

## Purpose
`shrinker.c` connects UBIFS TNC memory usage to the Linux VM shrinker. It frees clean znodes from mounted UBIFS instances when the kernel asks for reclaim and nudges background commits when no clean znodes are available but dirty znodes could become reclaimable after commit.

## Important APIs, Types, And Functions
Global state includes `ubifs_infos`, protected by `ubifs_infos_lock`, `shrinker_run_no` for fair per-run iteration, and `ubifs_clean_zn_cnt`, the global clean-znode estimate used by the shrinker count path. `shrink_tnc()` walks one filesystem's TNC in level order, freeing old enough clean subtrees with `ubifs_destroy_tnc_subtree()` and updating both global and per-filesystem clean counts. `shrink_tnc_trees()` iterates all mounted filesystems, try-locking `umount_mutex` and `tnc_mutex`, moving processed instances to the list tail for fairness.

`kick_a_thread()` looks for mounted writable filesystems with dirty znodes and a resting commit state, then requests a background commit so dirty znodes can later become clean and reclaimable. `ubifs_shrink_count()` reports the global clean-znode count, tolerating temporary negative values by returning `1`. `ubifs_shrink_scan()` is the registered scan callback: it first tries old znodes, then young znodes, then any clean znodes, and returns `SHRINK_STOP` on contention with no progress.

## Control Flow
The VM asks for a count through `ubifs_shrink_count()` and a scan through `ubifs_shrink_scan()`. If no clean znodes exist, UBIFS may request a background commit and tells VM to retry later. If clean znodes exist, reclaim proceeds across mounted instances. Each instance is protected from unmount with `umount_mutex`, and its TNC is protected with `tnc_mutex`. Subtrees are reclaimed only when their root is clean, not in the commit `cnext` list, and old enough for the current age pass.

## State And Persistence
The shrinker mutates only memory-resident cache state: TNC znodes and clean-znode counters. It does not alter persistent media. However, by kicking background commits it can indirectly cause future commit IO. It must respect commit state because clean znodes on `c->cnext` have just been written but are still owned by the commit-end cleanup path.

## Dependencies And Integration Points
`super.c` registers the shrinker during module init and maintains `ubifs_infos` membership during mount/unmount. `tnc_misc.c` provides `ubifs_tnc_levelorder_next()` and subtree destruction. TNC commit code manipulates `cnext`, dirty/clean flags, and clean counters that the shrinker observes. Commit code and background thread handling provide `ubifs_request_bg_commit()` and commit state transitions.

## Risks And Edge Cases
The global and per-filesystem clean counters can be temporarily inconsistent or negative because commit cleanup and dirtying are concurrent. Reclaim must avoid znodes in `cnext` because that list is intentionally not protected by the normal TNC mutex. Try-lock failure should signal contention rather than blocking VM reclaim on unmount or TNC mutation. Freeing a subtree assumes level-order age monotonicity: if a root is old and clean, descendants are also old enough. Any bug in counter updates can lead to under-reporting reclaimable memory or `WARN_ON()` at module exit.

## Test Signals
Signals include memory pressure causing clean znode reclamation, reclaim during unmount, reclaim during commit with `cnext` populated, dirty-only TNCs causing background commit requests, fairness across multiple mounted volumes, age-threshold behavior, negative global clean-count tolerance, and module exit warnings for non-empty `ubifs_infos` or nonzero `ubifs_clean_zn_cnt`.
