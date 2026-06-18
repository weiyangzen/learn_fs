# Group Research: group_749_linux_sources_os_linux_linux_fs_f2fs_file_c_sources_os_linux_linux_f_47650bc24602

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/file.c -->
# File Research: sources/os/linux/linux/fs/f2fs/file.c

Read completely: 5491 lines.

## Summary
Implements F2FS VFS-facing regular-file behavior: mmap faults, page-mkwrite, fsync, llseek, open/release/flush, truncate, fallocate, file attributes, ioctl dispatch, direct and buffered read/write paths, splice read, fadvise, atomic-write controls, compression controls, device trim, GC/checkpoint user ioctls, and shutdown handling.

## Main Responsibilities
- Provides `f2fs_file_operations` and `f2fs_file_inode_operations`.
- Handles roll-forward-safe fsync and checkpoint fallback decisions.
- Implements truncation, hole punching, zero/collapse/insert range, preallocation, and block-range movement.
- Exposes F2FS-specific ioctls for atomic writes, GC, defrag, move range, flush device, resize, pinning, compression, verity, encryption, secure trim, and labels.
- Chooses between buffered I/O and iomap direct I/O.
- Maintains file flags, project quota, pin-file state, direct-I/O alignment reporting, and extent precaching.
- Coordinates with compression, encryption, verity, quota, checkpoint, GC, multi-device, zoned, and atomic-write subsystems.

## Key APIs
- Operations tables: `f2fs_file_operations`, `f2fs_file_inode_operations`, `f2fs_file_vm_ops`.
- Sync/mmap/open: `f2fs_sync_file()`, `f2fs_file_mmap_prepare()`, `f2fs_file_open()`, `f2fs_release_file()`, `f2fs_file_flush()`.
- Truncate/fallocate: `f2fs_truncate()`, `f2fs_truncate_blocks()`, `f2fs_truncate_hole()`, `f2fs_fallocate()`.
- Ioctl dispatch: `f2fs_ioctl()`, `f2fs_compat_ioctl()`, `__f2fs_ioctl()`.
- Atomic writes: `f2fs_ioc_start_atomic_write()`, `f2fs_ioc_commit_atomic_write()`, `f2fs_ioc_abort_atomic_write()`.
- Data I/O: `f2fs_file_read_iter()`, `f2fs_file_write_iter()`, `f2fs_dio_read_iter()`, `f2fs_dio_write_iter()`.
- Admin/control helpers: `f2fs_do_shutdown()`, `f2fs_precache_extents()`, `f2fs_pin_file_control()`.

## Important Behavior
`f2fs_do_sync_file()` first writes dirty data, then decides whether the file can be recovered by roll-forward node logging or needs a full checkpoint. Checkpoint is forced for non-regular files, compressed files, hardlinks, wrong parent inode tracking, low roll-forward space, strict fsync directory recovery, fastboot, and other global conditions.

`f2fs_vm_page_mkwrite()` converts inline data, allocates or verifies a backing block, waits for writeback and GC writeback, zeroes EOF fragments, and marks the folio dirty. Large folios are explicitly rejected for write faults.

Truncation clears dnode block addresses, invalidates physical blocks, updates read and age extent caches, handles compressed cluster alignment, clears partial EOF data, and converts inline data when the new size no longer fits inline storage.

Fallocate supports punch hole, collapse range, zero range, insert range, and preallocation. Pinned and compressed files reject partial range transforms. Pinned-file expansion allocates section-aligned pinned blocks and may trigger foreground GC.

Block exchange helpers power collapse/insert/move/defrag paths. They read source block addresses, optionally replace uncheckpointed blocks, clone or copy data, roll back partial failures, and update inode size.

The ioctl table is broad. It includes atomic write lifecycle, shutdown modes, FITRIM, fscrypt policy/key calls, GC and GC range, checkpoint write, defragment, move range, flush device, feature query, pin-file controls, extent precache, resize, fs-verity, filesystem label, compression block release/reserve, secure trim, compression options, user-triggered compress/decompress, device-alias query, and I/O priority hints.

Direct I/O is disabled or falls back to buffered I/O for unsupported fscrypt DIO, verity, compression, inline reads, unaligned multi-device layouts, non-pinned zoned writes, checkpoint-disabled mode, and compatible misalignment cases. Partial direct writes fall back to buffered writes and flush/drop page cache to preserve O_DIRECT semantics.

## State and Synchronization
Uses inode locks, `i_gc_rwsem[READ/WRITE]`, `f2fs_lock_op()`, filemap invalidate locks, folio locks, `pin_sem`, `gc_lock`, `sb_lock`, quota transfers under operation locking, writeback counters, and atomic/COW inode references. Many paths wait for direct I/O, data writeback, node writeback, or block writeback before moving or invalidating blocks.

## Risks
This file is the main policy junction for user-visible file behavior. Lock ordering across inode locks, filemap invalidate locks, `i_gc_rwsem`, `gc_lock`, and `f2fs_lock_op()` is critical. Range transforms and move operations are vulnerable to partial failure, stale block-address validation, and rollback mistakes. Compression release/reserve and user-triggered compress/decompress can leave partially transformed files and intentionally mark the filesystem for fsck in some failure cases. Direct-I/O fallback must preserve O_DIRECT semantics while still allowing legacy buffered fallback behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/gc.c -->
# File Research: sources/os/linux/linux/fs/f2fs/gc.c

Read completely: 2426 lines.

## Summary
Implements F2FS garbage collection, including the background GC kernel thread, victim selection policies, age-threshold GC, SSR victim lookup support, pinned-section handling, node/data block migration, GC range execution, GC manager setup, and filesystem shrink/resize support.

## Main Responsibilities
- Starts, stops, and runs the background GC thread.
- Selects victim segments/sections for background GC, foreground GC, SSR, and age-threshold GC.
- Maintains temporary victim rb-trees for age-based selection.
- Migrates valid node and data blocks out of victim segments.
- Handles pinned files and pinned sections during GC.
- Reclaims sections until free-space requirements are met, checkpointing when needed.
- Provides GC over explicit ranges and supports online filesystem shrink.

## Key APIs
- Thread lifecycle: `f2fs_start_gc_thread()`, `f2fs_stop_gc_thread()`, `gc_thread_func()`.
- Victim selection: `f2fs_get_victim()`, `select_policy()`, `get_gc_cost()`, `lookup_victim_by_age()`.
- Migration: `gc_node_segment()`, `gc_data_segment()`, `move_data_block()`, `move_data_page()`, `ra_data_block()`.
- Main GC flow: `f2fs_gc()`, `do_garbage_collect()`, `f2fs_gc_range()`.
- Resize/shrink: `f2fs_resize_fs()`, `free_segment_range()`, `update_sb_metadata()`, `update_fs_metadata()`.
- Cache lifecycle: `f2fs_create_garbage_collection_cache()`, `f2fs_destroy_garbage_collection_cache()`.
- Setup: `f2fs_build_gc_manager()`.

## Important Behavior
The GC thread adapts sleep time based on urgent modes, free space, dirty/invalid block ratios, zoned-device thresholds, foreground-GC merge requests, and I/O idleness. It acquires `gc_lock`, chooses foreground or background mode, calls `f2fs_gc()`, wakes merged foreground waiters, and periodically balances metadata.

Victim selection supports greedy, cost-benefit, age-threshold GC, SSR, and AT_SSR. It scans dirty bitmaps, honors max-search limits, skips current sections and busy sections, handles checkpoint-disabled constraints, avoids background-selected victims unless foreground GC can consume them, and tracks `last_victim` cursors.

Age-threshold GC stores candidate sections in a temporary rb-tree ordered by mtime, then combines age and utilization cost. AT_SSR searches around a target age and prioritizes low checkpoint-valid block counts.

Node GC validates summary NAT information, readaheads NAT and node pages in phases, verifies the current NAT block address still points at the victim block, then rewrites node folios cold.

Data GC is phased: NAT readahead, node readahead, liveness validation, inode/data readahead, then migration. It validates that the node still references the victim block, obtains the owning inode, avoids inline-data contradictions, handles meta-inode GC through `META_MAPPING`, and migrates either by page writeback or direct block copying.

`f2fs_gc()` escalates to foreground GC when free sections are insufficient, checkpoints prefree segments when that can reclaim space, loops until requirements are met, and stops after too many skipped inode GC locks by checkpointing. It unpins pinned sections after foreground GC.

Resize shrink first dry-runs evacuation of the tail sections, freezes the filesystem, updates in-memory and on-disk geometry, commits the superblock, updates checkpoint-visible metadata, writes a resize checkpoint, and marks fsck-needed on recovery failures.

## State and Synchronization
Uses `gc_lock`, dirty segment list mutex, SIT sentry locks, pinned section bitmaps, victim section bitmaps, `next_victim_seg`, `cur_victim_sec`, radix-tree GC inode lists, folio locks, `i_gc_rwsem`, direct-I/O waits, blk plugs, checkpoint locks, freeze/thaw, and superblock locks. Victim entries are allocated from `f2fs_victim_entry`.

## Risks
GC correctness depends on summary, NAT, SIT valid maps, and node data addresses agreeing at migration time. Race handling is defensive, but stale or corrupted metadata can skip blocks, stop checkpoints, or set `SBI_NEED_FSCK`. Pinned files can repeatedly block foreground GC and are tracked as a risk signal. Resize has high blast radius because it temporarily changes `MAIN_SECS`, moves current segments, performs GC, mutates superblock geometry, and relies on checkpoint recovery.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/gc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/gc.h -->
# File Research: sources/os/linux/linux/fs/f2fs/gc.h

Read completely: 202 lines.

## Summary
Defines F2FS garbage-collection constants, background-GC thread state, temporary GC inode/victim structures, free-space accounting helpers, sleep-time adjustment helpers, and GC boost heuristics.

## Main Contents
- GC thread sleep defaults for regular and zoned devices.
- Age-threshold GC defaults: age threshold, candidate ratio, max candidates, age weight, and accuracy class.
- Invalid/free block percentage thresholds for background GC triggering.
- Zoned-device no-GC and boost-GC thresholds.
- Pinned-file and victim-search defaults.
- `struct f2fs_gc_kthread`.
- `struct gc_inode_list`.
- `struct victim_entry`.
- Inline helpers for free block accounting, sleep adjustments, and GC boost decisions.

## Important Behavior
`free_segs_blk_count_zoned()` sums usable blocks per free segment, accounting for zoned devices whose zone capacity can be smaller than zone size. Non-zoned accounting can use segment counts directly.

`free_user_blocks()` subtracts overprovisioned space from free segment blocks. `has_enough_invalid_blocks()` triggers background GC when invalid blocks are high and free user blocks are low. `need_to_boost_gc()` uses zoned free-block thresholds for zoned devices and invalid-block pressure for non-zoned devices.

Sleep helpers increase, decrease, or reset the GC thread wait interval within configured min/max/no-GC limits.

## Risks
The constants here directly tune GC aggressiveness and latency. Zoned devices depend on usable-block accounting rather than raw segment counts. Changing threshold defaults can alter write amplification, free-space recovery latency, and foreground-GC frequency.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/gc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/hash.c -->
# File Research: sources/os/linux/linux/fs/f2fs/hash.c

Read completely: 137 lines.

## Summary
Implements F2FS filename hashing. It uses the ext3-derived TEA hash for ordinary names and casefold-aware handling for Unicode and encrypted directories.

## Main Responsibilities
- Converts byte strings into TEA hash input words.
- Computes the F2FS directory hash value.
- Handles `.` and `..` specially.
- Hashes casefolded names when casefolding is enabled.
- Uses fscrypt SipHash for encrypted casefolded plaintext names.

## Key APIs
- `f2fs_hash_filename()`.
- Internal helpers: `TEA_transform()`, `str2hashbuf()`, `TEA_hash_name()`.

## Important Behavior
The TEA hash initializes with fixed ext-style seed values, processes names in 16-byte chunks, and masks out `F2FS_HASH_COL_BIT`.

For casefolded directories, the function prefers the precomputed Unicode casefolded name. If the name is invalid Unicode or otherwise lacks `cf_name`, it hashes the user-supplied plaintext name as opaque bytes. For encrypted casefolded directories, it hashes plaintext through `fscrypt_fname_siphash()` instead of hashing ciphertext.

`name_is_dot_dotdot()` returns hash zero for `.` and `..`.

## Risks
Directory lookup correctness depends on hashing the same logical name representation that insertion used. Casefolded encrypted directories are especially sensitive: falling back to `usr_fname` rather than `disk_name` is required so ciphertext does not determine casefold lookup hashes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/inline.c -->
# File Research: sources/os/linux/linux/fs/f2fs/inline.c

Read completely: 850 lines.

## Summary
Implements inline data and inline directory support. It decides when inline storage is valid, reads/writes inline file data from inode nodes, converts inline files/directories to regular block-backed layout, recovers inline data during roll-forward, supports inline directory lookup/mutation/readdir, and reports inline extents through fiemap.

## Main Responsibilities
- Determines whether a file, symlink, or directory may use inline storage.
- Validates inline-data consistency during inode sanity checks.
- Reads, writes, truncates, converts, and recovers inline file data.
- Converts inline directories to block-backed directories when they run out of inline slots.
- Adds, deletes, finds, checks emptiness, and reads inline directory entries.
- Emits inline fiemap extents.

## Key APIs
- Inline data policy: `f2fs_may_inline_data()`, `f2fs_sanity_check_inline_data()`, `f2fs_may_inline_dentry()`.
- Inline data I/O: `f2fs_read_inline_data()`, `f2fs_write_inline_data()`, `f2fs_truncate_inline_inode()`.
- Conversion/recovery: `f2fs_convert_inline_inode()`, `f2fs_convert_inline_folio()`, `f2fs_recover_inline_data()`.
- Inline directories: `f2fs_find_in_inline_dir()`, `f2fs_make_empty_inline_dir()`, `f2fs_try_convert_inline_dir()`, `f2fs_add_inline_entry()`, `f2fs_delete_inline_entry()`, `f2fs_empty_inline_dir()`, `f2fs_read_inline_dir()`.
- Reporting: `f2fs_inline_data_fiemap()`.

## Important Behavior
Inline data is allowed only for regular files and symlinks, not atomic-write users, and only while size fits `MAX_INLINE_DATA()`. Files requiring post-read processing, such as encryption/verity paths, are excluded from normal inline-data use.

`f2fs_convert_inline_folio()` reserves a real block, copies inline bytes to page cache, writes them out-of-place, waits for writeback, marks append-write recovery state, then clears inline data and flags. It treats a non-`NEW_ADDR` first block after reservation as corruption.

Inline recovery reconciles previous and recovered inline flags: keep inline data, drop inline data and recover blocks, truncate blocks and restore inline data, or recover normal blocks.

Inline directory conversion has two paths. Level-zero directories copy the inline dentry structure into a newly allocated dentry block. Rehashed directories back up inline dentries, clear inline storage, re-add entries through normal insertion, and restore the inline backup on failure.

Inline directory mutation updates the inode node directly, initializes new child inode metadata when needed, maintains parent metadata, and clears bitmap slots on delete.

`f2fs_inline_data_fiemap()` reports inline data as `FIEMAP_EXTENT_DATA_INLINE`, optionally syncing the inode node first, and computes the byte address relative to the inode node block when known.

## State and Synchronization
Uses inode-node folios, data folios, folio writeback waits, `f2fs_lock_op()`, inode `i_sem` for child metadata initialization, dirty inode/page accounting, inline xattr size compatibility state, and normal dentry helpers from `dir.c`.

## Risks
Inline conversion must preserve data while switching on-disk layout and recovery flags. Directory conversion can fail mid-rehash and must restore the inline dentry image. Inline-data sanity checks are important because inline flags must never coexist with real block pointers or incompatible inode types/features.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/inline.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/inode.c -->
# File Research: sources/os/linux/linux/fs/f2fs/inode.c

Read completely: 1066 lines.

## Summary
Implements F2FS inode loading, validation, flag restoration, checksum calculation, inode writeback, eviction, failed-new-inode cleanup, and VFS operation assignment. It translates on-disk `struct f2fs_inode` fields into `struct inode` and `struct f2fs_inode_info`, then writes in-memory state back to inode node pages.

## Main Responsibilities
- Marks inodes dirty using F2FS dirty-inode policy.
- Maps F2FS inode flags to VFS inode flags.
- Encodes and decodes special-file device numbers.
- Computes, verifies, and sets inode checksums.
- Validates on-disk inode metadata, feature dependencies, inline state, compression state, xattr state, project quota state, and device-alias state.
- Reads inode fields and initializes extent caches/stat counters.
- Instantiates inode operation tables for regular files, directories, symlinks, special files, and meta inodes.
- Writes inode state back to node folios.
- Evicts inodes, truncates deleted inode data, drops quotas/extents/compression cache, and removes inode node pages.
- Handles failed inode creation by syncing, orphaning, or freeing the NID.

## Key APIs
- Dirty/flags: `f2fs_mark_inode_dirty_sync()`, `f2fs_set_inode_flags()`.
- Checksum: `f2fs_inode_chksum_verify()`, `f2fs_inode_chksum_set()`.
- Load: `f2fs_iget()`, `f2fs_iget_retry()`, `do_read_inode()`.
- Writeback: `f2fs_update_inode()`, `f2fs_update_inode_page()`, `f2fs_write_inode()`.
- Eviction/failure: `f2fs_evict_inode()`, `f2fs_handle_failed_inode()`, `f2fs_remove_donate_inode()`.

## Important Behavior
`do_read_inode()` reads the inode node folio, populates mode, uid/gid, nlink, size, block count, timestamps, generation, depth or GC failures, xattr nid, flags, advice, parent inode, directory level, inline flags, extra-attribute size, inline-xattr size, project id, creation time, compression fields, extent cache state, and stats.

`sanity_check_inode()` rejects corrupted or unsupported combinations: zero block count, mismatched inode footer ino/nid, self-referential xattr nid, directory nlink of one, invalid extra-attr size, compression inconsistency, invalid inline-xattr size, feature flags without extra-attr support, invalid inline data/dentry state, casefold without feature support, invalid xattr nid range, and device-alias without feature or pin flag.

`f2fs_iget()` forbids exposing meta inodes through ordinary iget hits, assigns address-space operations for node/meta/compress inodes, and assigns file/dir/symlink/special inode operations for normal inodes.

`f2fs_update_inode()` serializes current in-memory inode state into the raw inode, including read extent, inline flags, timestamps, depth/GC failures, xattr nid, flags, project id, creation time, compression metadata, rdev encoding, and checksum. Atomic files avoid writing size except after atomic commit.

`f2fs_write_inode()` skips meta inodes, avoids unnecessary lazytime-only updates, returns `-EIO` on checkpoint error, re-dirties when checkpoint is not ready, updates the inode page, and balances the filesystem when called with writeback pressure.

`f2fs_evict_inode()` aborts atomic writes, releases COW inodes, drops page cache, invalidates compression cache, removes dirty/donate state, destroys extents, truncates deleted inode data, removes inode node pages, repairs dirty state on failure, drops quota, updates stats, invalidates node/xattr pages, and restores append/update inode tracking for still-linked inodes.

Failed inode creation clears nlink, writes/syncs the inode page, unlocks the new inode, then either adds it to the orphan list or marks its NID free depending on NAT state.

## State and Synchronization
Uses inode node folios, node writeback waits, extent-tree locks, inode dirty flags, quota initialization/drop, orphan inode tracking, checkpoint state, compression counters, donate inode lists, COW inode references, and freeze protection during deletion.

## Risks
Inode loading is a trust boundary for on-disk metadata. Missing a feature dependency or corrupted field can later corrupt block accounting, xattr lookup, compression state, or directory behavior. Eviction must handle many partially failed states without leaving dirty inode-list entries or leaked orphan/NID state. Atomic-write and COW inode lifetimes are especially sensitive because inode size and dirty state have special commit rules.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/inode.c -->