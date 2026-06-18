# subset-b-005661 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/segment.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/segment.c

## Purpose
`segment.c` is the main F2FS segment-management implementation. It owns active-log segment allocation, SSR/LFS switching, SIT updates, dirty and prefree segment transitions, discard/trim scheduling, flush merging, summary checkpoint I/O, atomic-write block replacement, zoned-device write-pointer repair, and mount/unmount construction/destruction of segment-manager state.

## Important APIs, types, and functions
The public surface includes `f2fs_need_SSR`, `f2fs_balance_fs`, `f2fs_balance_fs_bg`, `f2fs_issue_flush`, `f2fs_create_flush_cmd_control`, `f2fs_destroy_flush_cmd_control`, `f2fs_flush_device_cache`, `f2fs_dirty_to_prefree`, `f2fs_get_unusable_blocks`, `f2fs_disable_cp_again`, `f2fs_clear_prefree_segments`, `f2fs_start_discard_thread`, `f2fs_issue_discard_timeout`, `f2fs_trim_fs`, `f2fs_allocate_data_block`, `f2fs_do_write_meta_page`, `f2fs_do_write_node_page`, `f2fs_outplace_write_data`, `f2fs_inplace_write_data`, `f2fs_replace_block`, `f2fs_do_replace_block`, `f2fs_flush_sit_entries`, `f2fs_build_segment_manager`, and `f2fs_destroy_segment_manager`.

Atomic-write support is handled by `f2fs_commit_atomic_write`, `__f2fs_commit_atomic_write`, `__replace_atomic_write_block`, `__complete_revoke_list`, and `f2fs_abort_atomic_write`. These functions replace blocks from a COW inode into the target inode, track old addresses in `struct revoke_entry`, and roll changes back if a replacement fails.

Flush and discard support is split between `struct flush_cmd_control` and `struct discard_cmd_control`. Flush merging uses `issue_flush_thread`, `flush_cmd`, an llist, completions, and `blkdev_issue_flush`. Discard uses `struct discard_cmd`, `struct discard_info`, red-black tree lookup/merge helpers, pending/wait/fstrim lists, `issue_discard_thread`, and slab caches for discard commands and checkpoint discard-entry staging.

Segment and SIT mutation centers on `update_sit_entry`, `update_sit_entry_for_alloc`, `update_sit_entry_for_release`, `update_segment_mtime`, `locate_dirty_segment`, `__locate_dirty_segment`, `__remove_dirty_segment`, `set_prefree_as_free_segments`, `get_new_segment`, `new_curseg`, `change_curseg`, `get_ssr_segment`, and `need_new_seg`. Mount-time initialization uses `build_sit_info`, `build_free_segmap`, `build_curseg`, `build_sit_entries`, `init_free_segmap`, `build_dirty_segmap`, `sanity_check_curseg`, and `init_min_max_mtime`.

Checkpoint summary and SIT persistence is handled by `read_compacted_summaries`, `read_normal_summaries`, `restore_curseg_summaries`, `write_compacted_summaries`, `write_normal_summaries`, `f2fs_write_data_summaries`, `f2fs_write_node_summaries`, `get_next_sit_folio`, `remove_sits_in_journal`, and `f2fs_flush_sit_entries`.

## Control flow
Write allocation flows through `do_write_page`. The code classifies the I/O into a curseg type using the active-log policy (`2`, `4`, or `6` logs), inode temperature flags, write-life hints, cold/compressed-file state, GC state, and age extent cache. `f2fs_allocate_data_block` then locks `curseg_lock`, the selected `curseg_mutex`, and `sit_i->sentry_lock`, waits for any discard covering the new address, writes the summary entry, advances `next_blkoff`, updates segment mtimes, increments the new SIT bit, decrements the old SIT bit, closes full segments, and either allocates a new LFS segment or switches to an SSR segment. Finally it updates dirty-segment maps and queues the I/O in the appropriate write bio list.

Allocation chooses between LFS and SSR. `f2fs_need_SSR` returns true when free sections fall below dirty node/dentry/imeta demand plus reserved/min-SSR sections, when checkpoints are disabled, or during urgent GC. `need_new_seg` prefers new LFS segments when space permits or when the next segment is free; otherwise it lets `get_ssr_segment` select a victim through the GC victim selector. `new_curseg` persists the old summary page, asks `get_new_segment` for a free segment/section, marks it in use, resets the current segment, and marks its SIT type. `change_curseg` reuses an existing dirty/prefree segment for SSR, reloads its summary block, and positions `next_blkoff` at the next uncheckpointed and currently free slot.

SIT mutation is synchronous under `sentry_lock`. Invalidations call `f2fs_invalidate_blocks`, which can handle a range across multiple segments, updates mtimes, clears valid-map bits, adjusts `written_valid_blocks`, updates section counters, and calls `locate_dirty_segment`. Allocations call the same `update_sit_entry` path with positive deltas. The dirty-list path classifies segments as `DIRTY`, typed dirty (`DIRTY_HOT_DATA` through `DIRTY_COLD_NODE`), or `PRE` when they become fully obsolete and checkpoint-safe.

Checkpoint flow flushes dirty SIT entries either into the SIT journal in the cold-data current summary or into alternating SIT blocks. `f2fs_flush_sit_entries` groups dirty segment entries by SIT block, falls back from journal to full SIT folio writes when journal space is insufficient or resize is active, records discard candidates, validates block counts, clears dirty bits, and then promotes prefree segments into the free map. Summary checkpoint flow serializes the current data summaries compactly when `CP_COMPACT_SUM_FLAG` is set and always writes node summaries in normal form.

Discard flow starts when checkpoint/SIT flushing or prefree cleanup discovers invalidated block ranges. `__update_discard_tree_range` inserts or merges ranges in the discard rb-tree and length-bucket pending lists. The background discard thread builds a policy based on idle state, free memory, utilization, and urgent GC, then issues either ordered rb-tree ranges or length-prioritized pending-list ranges. Each submitted discard or zone reset owns a completion, refcount, state transition from `D_PREP` to `D_SUBMIT`/`D_PARTIAL` to `D_DONE`, and an endio callback. Fstrim forces a checkpoint to materialize trim candidates, then issues and waits for the relevant range unless realtime discard is enabled.

Flush flow either submits directly or merges concurrent flush requests. With `FLUSH_MERGE`, the first or multi-device flush submits directly while later single-device requests are appended to an llist for `issue_flush_thread`; one physical flush completion is then broadcast to all waiting `flush_cmd` completions.

Mount flow allocates `f2fs_sm_info`, creates flush/discard controls, builds SIT/free/curseg state, restores summaries from checkpoint, reads SIT entries plus SIT journal overrides, initializes free and dirty maps, checks curseg consistency, and seeds mtime ranges. Unmount destroys controls and state in reverse, including a final discard-timeout attempt before freeing discard control.

## State and persistence behavior
The persistent state managed here is the SIT, summary area, current segment metadata in checkpoint, checkpoint SIT bitmap, and checkpoint flags such as compact summaries and trimmed state. Runtime-only state includes curseg locks and summary buffers, free/dirty/prefree bitmaps, discard rb-tree/list state, flush queues, mtime min/max ranges, in-memory pinned/ATGC cursegs, device dirty bits, and slab-allocated helper objects.

`seg_entry` valid maps and counts mirror the on-disk SIT but are updated eagerly before I/O submission so allocation and SSR victim decisions see current state. `ckpt_valid_map` and `ckpt_valid_blocks` preserve last-checkpoint state and are especially important when checkpoints are disabled: releasing a checkpointed block increases `sbi->unusable_block_count`, and SSR must not reuse data that belongs to the previous checkpoint image.

SIT persistence is double-buffered. `current_sit_addr` selects the active half using the checkpoint SIT bitmap, `get_next_sit_folio` writes the alternate half, and `set_to_next_sit` toggles the bitmap. Summary persistence records enough information to reconstruct active logs and journal entries after mount, with compacted summaries optimizing the hot/warm/cold data logs.

Discard persistence is indirect. Discard commands are not themselves durable, but checkpoint trim flags, SIT validity, and `discard_map` reconstruction determine whether future mounts need to reissue block-unit discards. On unmount, `f2fs_issue_discard_timeout` tries to drain or drop queued commands within the timeout policy.

Zoned-device state is partly external to F2FS. `f2fs_check_and_fix_write_pointer` validates curseg write pointers and all sequential zones against SIT validity, allocating new sections, resetting empty zones, or finishing/filling zones with valid data whose write pointer does not match expected state.

## Dependencies and integration points
The file depends on core F2FS structures from `f2fs.h`, segment definitions from `segment.h`, node helpers from `node.h`, GC victim selection from `gc.h`, and iostat/trace infrastructure. It integrates with VFS writeback, folios, BIO submission, block-layer flush/discard/zone-management APIs, rwsems, mutexes, spinlocks, wait queues, completions, kthreads, freezable threads, slab caches, fault injection, and kernel memory-reclaim helpers.

Important cross-file contracts include NAT/free-nid balancing (`node.c`), extent-cache age decisions, GC victim selection (`f2fs_get_victim`, `f2fs_gc`, `f2fs_gc_range`), checkpoint orchestration (`f2fs_write_checkpoint`, `f2fs_sync_fs`), roll-forward and node summary restoration, direct and buffered data write paths, multi-device dirty tracking, sysfs-tunable discard/IPU/fragmentation policies, and mount error handling through `f2fs_handle_error`, `SBI_NEED_FSCK`, and checkpoint stop reasons.

## Risks
The main correctness risk is divergence among SIT valid counts, current/ckpt bitmaps, section aggregates, dirty maps, and free maps. Bugs here can cause block reuse while data is still live, ENOSPC despite free space, corrupt SSR reuse, or mount-time fsck requirements. The code has many `f2fs_bug_on`, `check_block_count`, and consistency checks because the invariants are tight.

Concurrency risk is high. Allocation, invalidation, checkpoint flushing, discard completion, GC, resize, and atomic commit all touch overlapping state. Lock order across `curseg_lock`, `curseg_mutex`, `sentry_lock`, `seglist_lock`, discard `cmd_lock`, and device locks must remain consistent. Discard commands also have independent BIO refcounts and completions, so changing command removal or punch behavior can race with endio or fstrim waits.

Atomic-write commit risk centers on partial replacement. `__f2fs_commit_atomic_write` must preserve enough revoke entries to undo already-swapped blocks, correctly account valid-block counts between target and COW inodes, and truncate holes for replace-mode commits. Fault-injection paths and ENOMEM retry behavior are important because failure after some replacements must leave the file and SIT consistent.

Discard risk includes issuing discard over valid blocks, losing queued ranges during rb-tree merge/split, overcounting `undiscard_blks`, mishandling unsupported discard devices, and treating sequential-zone resets like regular discard. Fstrim and unmount policies intentionally may not wait for every background discard in realtime-discard mode, so visible trim byte counts and actual queued work differ.

Zoned-device risk includes write-pointer/SIT disagreement, partial-zone capacity handling, pinned section allocation on sequential zones, and alignment requirements for zone reset. The code has separate paths for power-on recovery and regular operation, so regressions can be mount-mode dependent.

## Test signals
Useful signals include mount with corrupted SIT valid counts, SIT journal entries with invalid segnos, summary restore with compact and normal checkpoint packs, SSR allocation under low-free-section pressure, checkpoint-disabled writes and invalidations, atomic commit success/failure/fault injection, large-section dirty section accounting, block-unit discard reconstruction with and without `CP_TRIMMED_FLAG`, fstrim with realtime discard both enabled and disabled, multi-device flush/device-dirty behavior, and background balance under NAT/free-nid/extent pressure.

Zoned tests should cover conventional plus sequential mixed devices, unaligned write pointers after unsafe shutdown, empty zones with nonzero write pointers, valid zones needing finish/zeroout, pinned-section allocation fallback through GC, and partial zone-capacity sections. Concurrency tests should exercise GC and checkpoint racing with allocation, discard endio racing with new allocations in the same range, and unmount while discard/flush threads have pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/segment.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/segment.h -->
# sources/distributed-fs/ceph-client/fs/f2fs/segment.h

## Purpose
`segment.h` defines the core constants, address-conversion macros, policy enums, state structures, and inline helpers used by F2FS segment management. It is the contract between allocation, GC, checkpoint, discard, and writeback code for translating block addresses into segments/sections/zones and for maintaining SIT, free-map, dirty-map, curseg, summary, and IPU policy state.

## Important APIs, types, and functions
Important constants include `NULL_SEGNO`, `NULL_SECNO`, `F2FS_MIN_SEGMENTS`, `F2FS_MIN_META_SEGMENTS`, `INVALID_MTIME`, `DEF_RECLAIM_PREFREE_SEGMENTS`, and `DEF_MAX_RECLAIM_PREFREE_SEGMENTS`. Address macros include `MAIN_BLKADDR`, `SEG0_BLKADDR`, `MAIN_SEGS`, `TOTAL_SEGS`, `MAX_BLKADDR`, `START_BLOCK`, `NEXT_FREE_BLKADDR`, `GET_SEGNO`, `GET_SEC_FROM_SEG`, `GET_SEG_FROM_SEC`, `GET_ZONE_FROM_SEC`, `GET_SUM_BLOCK`, and `SIT_BLOCK_OFFSET`.

Policy enums define allocation mode (`LFS`, `SSR`, `AT_SSR`), GC mode (`GC_CB`, `GC_GREEDY`, `GC_AT`, `ALLOC_NEXT`, `FLUSH_DEVICE`), foreground/background GC, and dirty-segment classes. IPU policy bits include force, SSR-triggered, utilization-triggered, fsync, async, no-cache, honor-OPU, and disabled modes.

The key structures are `struct victim_sel_policy`, `struct seg_entry`, `struct sec_entry`, `struct revoke_entry`, `struct sit_info`, `struct free_segmap_info`, `struct dirty_seglist_info`, `struct curseg_info`, and `struct sit_entry_set`. These structures hold GC-victim search parameters, per-segment validity maps and mtimes, section aggregates, atomic revoke entries, SIT cache and checkpoint bitmaps, free segment/section bitmaps, dirty/prefree/victim/pinned bitmaps, active log state, and grouped SIT flush accounting.

Important inline helpers include `CURSEG_I`, `is_curseg`, `is_cursec`, `get_seg_entry`, `get_sec_entry`, `get_valid_blocks`, `get_ckpt_valid_blocks`, `set_ckpt_valid_blocks`, `seg_info_from_raw_sit`, `seg_info_to_sit_folio`, `seg_info_to_raw_sit`, `find_next_inuse`, `__set_free`, `__set_inuse`, `__set_test_and_free`, `__set_test_and_inuse`, `get_sit_bitmap`, `free_segments`, `free_sections`, `prefree_segments`, `dirty_segments`, `__get_secs_required`, `has_not_enough_free_secs`, `f2fs_is_checkpoint_ready`, `utilization`, `curseg_segno`, `curseg_alloc_type`, `valid_main_segno`, `verify_fio_blkaddr`, `check_block_count`, `current_sit_addr`, `next_sit_addr`, `set_to_next_sit`, `get_mtime`, `set_summary`, `start_sum_block`, `sum_blk_addr`, `sec_usage_check`, `nr_pages_to_skip`, `nr_pages_to_write`, and `wake_up_discard_thread`.

## Control flow
Most functions in this header are small invariants used by `segment.c` and neighboring F2FS code. Address conversion starts from superblock or segment-manager fields, maps block addresses relative to `segment0_blkaddr`, then converts through logical-relative segment numbering using `FREE_I(sbi)->start_segno`. Section and zone helpers derive larger allocation/GC units from segment numbers.

Free-map updates use a set-bit means in-use convention for `free_segmap` and `free_secmap`. `__set_free` clears a segment bit, increments free segment count, and may clear the section bit if every usable segment in the section is free. `__set_inuse` sets segment and section bits and decrements counters. The test-and variants are used when state may already be in the desired condition and also reset cached next-victim hints when a whole section becomes free.

SIT conversion helpers load raw little-endian `f2fs_sit_entry` values into `seg_entry` caches and serialize them back during checkpoint. `check_block_count` walks the raw valid-map and verifies the encoded valid block count, segment boundary, and zoned usable-block limit. `current_sit_addr`, `next_sit_addr`, and `set_to_next_sit` implement the double-buffered SIT block selection protocol.

Space-reservation helpers compute whether checkpoints and foreground allocation have enough sections. `__get_secs_required` estimates additional sections needed for dirty node, dentry, imeta, and, in LFS checkpoint-disabled mode, data pages after subtracting room left in current logs. `has_not_enough_free_secs` combines that demand with reserved sections and caller-provided needs.

Writeback helpers tune batching: `nr_pages_to_skip` delays writeout to gather larger BIOs unless the backing device is already dirty-throttled, and `nr_pages_to_write` aligns asynchronous writeback toward BIO-sized or node-sized batches. `wake_up_discard_thread` wakes the discard thread only when pending commands meet granularity and idle conditions, unless forced.

## State and persistence behavior
The structures here distinguish durable checkpoint/SIT state from volatile caches. `seg_entry.cur_valid_map`, `valid_blocks`, and `mtime` are current runtime state that will be flushed to SIT. `seg_entry.ckpt_valid_map` and `ckpt_valid_blocks` preserve last-checkpoint state for SSR and checkpoint-disabled accounting. `sit_info.sit_bitmap` is a checkpoint-persisted selector for active SIT blocks, while `dirty_sentries_bitmap` and `sit_entry_set` are transient checkpoint-flush worklists.

`curseg_info` contains active-log state persisted through checkpoint summaries: segment number, allocation type, segment type, next block offset, summary entries, and journal contents. Its mutex and journal rwsem protect runtime mutation. In-memory-only active logs such as pinned and ATGC segments can be saved/restored around special operations.

Free and dirty maps are derived at mount from SIT and checkpoint summaries rather than directly stored as separate persistent objects. Dirty, prefree, victim, and pinned section maps guide GC and discard decisions until the next rebuild. `sec_entry` aggregates segment counts for large-section mode so GC and free-space decisions do not have to scan every segment repeatedly.

## Dependencies and integration points
The header depends on Linux block and backing-device interfaces and on F2FS global types from including translation units. It is included by segment management, GC, checkpoint, writeback, and node/data paths. It assumes definitions for `struct f2fs_sb_info`, `SM_I`, `SIT_I`, `FREE_I`, `DIRTY_I`, `F2FS_CKPT`, `F2FS_RAW_SUPER`, curseg constants, checkpoint flags, page counters, zoned-device helpers, and bitmap helpers.

It also integrates with block-layer write hints through IPU and temperature decisions, F2FS sysfs options (`active_logs`, discard unit, allocation mode), checkpoint-disabled state, large-section and zoned-volume layouts, and `CONFIG_F2FS_CHECK_FS` mirror/invalid-segment diagnostics.

## Risks
The macros in this header encode foundational address arithmetic. A wrong `start_segno`, segment0/main-area conversion, section rounding, or zoned capacity calculation can redirect allocation, discard, or SIT writes to the wrong area. This is especially sensitive for multi-device and zoned configurations where logical and device-local block addresses differ.

Free-map semantics are easy to misread because set bits mean in-use, not free. Counter updates must stay exactly paired with bitmap transitions, and section counters must account for unusable zoned tail segments. Current segments are deliberately excluded from some free/dirty transitions, so callers must know whether they are operating on current logs or closed segments.

SIT consistency risk is high. `valid_blocks`, `ckpt_valid_blocks`, section aggregates, raw SIT vblocks, current and checkpoint maps, and optional check-fs mirrors must agree. `check_block_count` and `sanity_check_valid_blocks` catch many problems, but only when those paths run.

Space-estimation helpers directly affect checkpoint readiness and foreground GC pressure. Underestimating required sections can lead to ENOSPC or checkpoint failure; overestimating can trigger unnecessary GC or writeback. The estimates depend on active log count and checkpoint-disabled/LFS modes.

## Test signals
Good coverage includes address conversion around `MAIN_BLKADDR`, last main segment, section and zone boundaries, large-section aggregation, zoned `CAP_BLKS_PER_SEC` and partial-capacity segments, and `current_sit_addr`/`next_sit_addr` toggling across both SIT halves. Free-map tests should verify segment and section counters for repeated set/free operations, current-section exclusions, unusable tail segments, and victim hint clearing.

SIT tests should inject raw valid-map/count mismatches, invalid segment numbers, invalid segment types, and check-fs mirror mismatches. Space tests should vary active log counts, dirty dentry/node/data pages, checkpoint-disabled mode, reserved sections, and LFS versus non-LFS allocation. Writeback signals include dirty-throttle behavior for `nr_pages_to_skip`, `nr_pages_to_write` changes in async writeback, and discard-thread wake decisions under idle and non-idle conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/segment.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/shrinker.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/shrinker.c -->
