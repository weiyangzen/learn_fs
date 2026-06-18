<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/gc.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/gc.c

## Purpose

`gc.c` implements F2FS garbage collection, victim selection, block relocation, background GC thread management, GC ioctl entry support, age-threshold GC management, section pinning, and filesystem shrink support. It is responsible for selecting dirty sections or segments, validating that summarized blocks are still live, migrating live node/data blocks elsewhere, freeing sections, coordinating with checkpoints, and handling special layouts such as large sections, zoned devices, multi-device filesystems, pinned files, atomic COW files, and metadata-backed data movement.

## Important APIs, Types, and Functions

- `f2fs_start_gc_thread()` and `f2fs_stop_gc_thread()` allocate, start, wake, stop, and free `struct f2fs_gc_kthread`.
- `gc_thread_func()` is the background daemon loop. It sleeps adaptively, reacts to foreground-merge waiters, urgent modes, zoned-device one-time GC, idle detection, freeze/read-only states, and calls `f2fs_gc()`.
- Victim policy is implemented by `select_gc_type()`, `select_policy()`, `get_max_cost()`, `get_cb_cost()`, `get_gc_cost()`, `check_bg_victims()`, age-tree helpers, and `f2fs_get_victim()`.
- Age-threshold GC uses `struct victim_entry`, an rb-tree ordered by mtime, and helpers `add_victim_entry()`, `atgc_lookup_victim()`, `atssr_lookup_victim()`, `lookup_victim_by_age()`, and `release_victim_entry()`.
- Pinned-section handling is provided by `f2fs_pin_section()`, `f2fs_pinned_section_exists()`, `f2fs_section_is_pinned()`, `f2fs_unpin_all_sections()`, and `f2fs_gc_pinned_control()`.
- Liveness and relocation helpers include `check_valid_map()`, `gc_node_segment()`, `f2fs_start_bidx_of_node()`, `is_alive()`, `ra_data_block()`, `move_data_block()`, `move_data_page()`, and `gc_data_segment()`.
- `do_garbage_collect()` migrates all selected segments in a section/window and submits merged writes.
- `f2fs_gc()` is the central GC control loop. It handles foreground escalation, prefree checkpoint reclamation, repeated victim selection, skipped-lock accounting, checkpoint fallback, pinned-section retries, and lock release.
- Initialization and cache hooks are `f2fs_create_garbage_collection_cache()`, `f2fs_destroy_garbage_collection_cache()`, `init_atgc_management()`, and `f2fs_build_gc_manager()`.
- Range and resize support is implemented by `f2fs_gc_range()`, `free_segment_range()`, `update_sb_metadata()`, `update_fs_metadata()`, and `f2fs_resize_fs()`.

## Control Flow and State Behavior

The background GC thread waits on its normal GC waitqueue, foreground-GC merge waitqueue, or explicit `gc_wake`. It skips work on read-only or frozen superblocks and acquires a write hold before checking whether GC should run. Urgent and foreground-merged paths take `gc_lock` directly. Normal background GC tries the lock, requires I/O idleness, then adjusts sleep time upward or downward based on free/invalid block pressure. It sets a `f2fs_gc_control` structure and calls `f2fs_gc()`, then wakes foreground waiters and runs background filesystem balancing.

Victim selection starts under `dirty_i->seglist_lock`. `select_policy()` chooses dirty bitmaps, search limits, granularity, and scan offsets based on LFS versus SSR allocation, GC type, segment type, large-section mode, random segment needs, and urgent/idle GC modes. Greedy GC minimizes valid block count, cost-benefit GC considers utilization and age, and ATGC/AT_SSR builds a temporary rb-tree of old candidate sections before choosing by age/utilization. Background victims can be remembered in `victim_secmap` for later foreground collection.

Data relocation is multi-phase. `gc_data_segment()` first readaheads NAT blocks, then node pages, then validates data liveness through `is_alive()`, then readaheads or pins inodes/data pages, and finally moves blocks. Liveness is checked by comparing summary entries, NAT node info, node page address slots, node versions, and valid maps. Regular data usually moves through page cache via `move_data_page()`, while metadata-inode or COW-related data can move through `META_MAPPING` via `move_data_block()` to preserve encrypted data and on-disk block contents. Node relocation in `gc_node_segment()` similarly verifies NAT addresses before moving node folios.

`f2fs_gc()` loops until enough sections are free or no useful victim remains. If free space is below thresholds, it escalates to foreground GC and may checkpoint to reclaim prefree segments. It tracks skipped rounds caused by inode GC semaphores and can checkpoint after excessive skip ratios. It clears current-victim state, unpins sections after foreground GC, releases `gc_lock`, drops cached GC inodes, and returns `-EAGAIN` for ioctl-style callers when no section was actually freed despite a skipped-error policy.

Resize flow first validates shrink size and feature constraints, then performs a dry-run segment evacuation while GC and checkpointing are locked. It freezes the superblock, repeats free-space checks, migrates live blocks out of the target range, updates raw superblock metadata, commits the superblock, adjusts in-memory FS metadata and checkpoint user block counts, writes a resize checkpoint, and rolls back metadata or marks `SBI_NEED_FSCK` on failure.

## Persistence, Locking, and Integration Points

GC mutates SIT valid maps, summary-derived block ownership, NAT-validated node/data locations, current segment allocation, victim history, pinned-section bitmaps, inode dirty/writeback state, and checkpoint state. It coordinates through `gc_lock`, `seglist_lock`, `sentry_lock`, `i_gc_rwsem`, `io_order_lock`, block plugs, page locks, mount freeze/write protection, and `cp_global_sem` during resize.

Dependencies include `f2fs.h`, `node.h`, `segment.h`, `gc.h`, `iostat.h`, NAT/SIT/SSA metadata, page cache and meta mapping, kthreads/freezer, blk plug, tracepoints, and F2FS allocation/writeback helpers. `file.c` calls into this file through GC ioctls, flush-device, resize, pinned file behavior, and free-space balancing. Segment allocation code calls `f2fs_get_victim()` for SSR-style target selection.

## Risks and Edge Cases

The hardest correctness risks are stale summaries, NAT/node mismatches, pinned files preventing relocation, races with SSR allocation making segments fully valid again, deadlocks between summary-page locks and SIT locks, and partial resize metadata updates. The code mitigates these with phase-separated readahead/validation/migration, valid-map rechecks, explicit lock ordering comments, pinned-section retry policy, checkpoint fallback, and `SBI_NEED_FSCK` on corruption. Zoned-device capacity differences and large-section migration windows complicate free-space accounting and victim progression.

## Test Signals

Important tests include background GC under idle and busy I/O, urgent GC modes, GC_MERGE foreground waiters, zoned-device one-time/boosted GC, ATGC and cost-benefit victim selection, SSR victim selection, pinned-file GC failures and unpin retry, corrupted summary/NAT mismatch handling, compressed and atomic-COW data migration, metadata inode GC, foreground GC under low-space pressure, checkpoint fallback after skipped locks, `F2FS_IOC_GARBAGE_COLLECT_RANGE`, flush-device relocation, and shrink/resize dry-run plus rollback failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/gc.c -->
