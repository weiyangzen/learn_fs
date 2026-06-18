# sources/distributed-fs/ceph-client/fs/f2fs/f2fs.h

## Purpose

`f2fs.h` is the central private header for the F2FS implementation in this source tree. It binds the F2FS on-disk definitions from the common kernel headers to the in-memory VFS-facing implementation by defining the core superblock, inode, node, segment, checkpoint, discard, IO, compression, quota, statistics, and feature helpers used by the rest of `fs/f2fs`.

The file is not a standalone algorithm module. Its role is to establish shared contracts: data structures carried across `super.c`, `inode.c`, `node.c`, `segment.c`, `checkpoint.c`, `data.c`, `dir.c`, `file.c`, `gc.c`, `recovery.c`, `compress.c`, `extent_cache.c`, `sysfs.c`, and debug/stat paths; inline helpers that must stay consistent with on-disk layout and locking; and prototypes for nearly every internal F2FS subsystem.

## Important APIs, Types, and Macros

### Mount, Feature, and Fault Contracts

- `enum f2fs_mount_opt`, `struct f2fs_mount_info`, `F2FS_OPTION()`, `set_opt()`, `clear_opt()`, and `test_opt()` define mount option storage and predicates. Options cover checkpoint behavior, discard, inline xattr/data/dentry, quota, compression, ATGC, GC merge, NAT bits, inline encryption, lazytime, and reserved node/root policies.
- `F2FS_FEATURE_*`, `F2FS_HAS_FEATURE()`, and generated helpers such as `f2fs_sb_has_encrypt()`, `f2fs_sb_has_blkzoned()`, `f2fs_sb_has_compression()`, and `f2fs_sb_has_packed_ssa()` wrap on-disk superblock feature bits.
- `CONFIG_F2FS_FAULT_INJECTION` adds `struct f2fs_fault_info`, fault types such as `FAULT_KMALLOC`, `FAULT_BLOCK`, `FAULT_CHECKPOINT`, and `FAULT_LOCK_TIMEOUT`, plus `time_to_inject()`. Allocation helpers and block/node accounting paths consult this to simulate failures.
- `f2fs_bug_on()` either hard BUGs under `CONFIG_F2FS_CHECK_FS` or warns and marks `SBI_NEED_FSCK` in production-style builds.

### Core In-Memory State

- `typedef u32 block_t` and `typedef u32 nid_t` intentionally mirror on-disk `__le32` block addresses and node IDs.
- `struct f2fs_sb_info` is the main mounted-filesystem state. It owns:
  - VFS and raw superblock pointers (`sb`, `raw_super`), checkpoint state (`ckpt`, `cur_cp_pack`, `cp_lock`, `cp_global_sem`, `cp_rwsem`, `cprc_info`), and special metadata inodes (`meta_inode`, `node_inode`).
  - Node and segment managers (`f2fs_nm_info`, `f2fs_sm_info`), write IO merge state (`write_io[]`, `io_order_lock`), page EIO retry accounting, inode tracking lists, extent cache roots, block/inode counters, reserved/unusable block counters, quota state, mount options, GC state, shrinker/sysfs state, multi-device/zoned state, checksum seed, error/stop-reason arrays, atomic-write counters, compression cache/statistics, and optional IO/stat instrumentation.
- `struct f2fs_inode_info` embeds `struct inode` and stores per-inode F2FS state: persisted inode flags, advice bits, directory depth or GC failure count, parent inode, ACL mode, internal FI flags, dirty-page accounting, xattr nid, last disk size, quota reservations, dirty/donate lists, atomic/COW inode links, extent trees, GC/xattr semaphores, extra inode attribute sizes, project ID, creation/disk times, compression parameters, writeback count, atomic write count, and optional fscrypt info.
- `struct f2fs_rwsem` wraps `struct rw_semaphore`, optionally using unfair-reader behavior and carrying F2FS lock names for trace/priority handling.

### Checkpoint, NAT/SIT, Discard, and Segment Types

- `struct cp_control`, `struct cp_stats`, `enum cp_time`, `enum f2fs_cp_phase`, and checkpoint reason flags (`CP_UMOUNT`, `CP_SYNC`, `CP_RECOVERY`, `CP_DISCARD`, etc.) describe checkpoint invocation and timing.
- `struct ckpt_req` and `struct ckpt_req_control` support merged/asynchronous checkpoint issuing through a checkpoint thread and low-level linked-list queue.
- `struct f2fs_nm_info` is the node/NAT manager state: NAT cache radix trees, NAT set cache, free nid roots/lists, NAT bitmaps, free-nid counts, NAT bits, and checkpoint bitmaps.
- `struct dnode_of_data` is the common cursor for locating and mutating a data block address through inode/direct/indirect node folios.
- `struct f2fs_sm_info` links SIT/free/dirty segment info, current segment array, curseg lock, area base addresses, segment counts, in-place-update thresholds, flush command control, and discard command control.
- `struct discard_entry`, `struct discard_cmd`, `struct discard_policy`, and `struct discard_cmd_control` model discard ranges, pending/in-flight discard commands, policy tuning, rbtree/list queues, and discard-thread state.
- `enum log_type`, `enum page_type`, `enum temp_type`, and `struct f2fs_io_info` encode data/node/meta write classes, hot/warm/cold temperature, bio operation flags, old/new block addresses, page/folio ownership, compression/encryption data, iostat classification, and writeback control.

### Directory, Inline, Extent, Compression, and Mapping Contracts

- `struct f2fs_filename` carries user, encrypted on-disk, hash, encryption scratch, and optional casefolded filename representations.
- `struct f2fs_dentry_ptr`, `make_dentry_ptr_block()`, and `make_dentry_ptr_inline()` normalize block dentry and inline dentry layouts for directory code.
- Inline-data macros (`MAX_INLINE_DATA`, `NR_INLINE_DENTRY`, `INLINE_DENTRY_BITMAP_SIZE`, `INLINE_RESERVED_SIZE`) depend on inode extra attributes and inline xattr address counts.
- `struct extent_info`, `extent_node`, `extent_tree`, and `extent_tree_info` define read and block-age extent caches, including largest read extent optimization and global shrinker lists.
- `struct f2fs_map_blocks` is the internal mapping result for block lookup/allocation and DIO/fiemap/bmap paths.
- Compression state is defined by `struct compress_data`, `compress_ctx`, `compress_io_ctx`, and `decompress_io_ctx`, plus compression algorithm/flag enums. These contexts track cluster index, raw/compressed pages, vmap buffers, lengths, fs-verity state, pending pages, refcounts, and work items.

### Inline Helpers With Behavioral Weight

- Container/access helpers: `F2FS_I()`, `F2FS_SB()`, `F2FS_I_SB()`, `F2FS_M_SB()`, `F2FS_F_SB()`, `F2FS_RAW_SUPER()`, `F2FS_CKPT()`, `F2FS_NODE()`, `F2FS_INODE()`, `NM_I()`, `SM_I()`, `SIT_I()`, `FREE_I()`, `DIRTY_I()`, `META_MAPPING()`, and `NODE_MAPPING()`.
- Checkpoint flag helpers use `cp_lock` when needed: `is_set_ckpt_flags()`, `set_ckpt_flags()`, `clear_ckpt_flags()`, `cur_cp_version()`, `cur_cp_crc()`, `__start_cp_addr()`, `__start_cp_next_addr()`, and `__set_cp_next_pack()`.
- Block/node accounting helpers (`get_available_block_count()`, `inc_valid_block_count()`, `dec_valid_block_count()`, `inc_valid_node_count()`, `dec_valid_node_count()`, valid inode counters) combine quota reservations, reserved-root/node logic, no-checkpoint unusable blocks, percpu counters, and `SBI_NEED_FSCK` consistency marking.
- Page/folio private-data helpers encode F2FS flags into `folio->private`/`page_private`: migration, inline inode, resource reference, atomic write, and private integer data.
- Inode state helpers (`set_inode_flag()`, `clear_inode_flag()`, `f2fs_i_blocks_write()`, `f2fs_i_size_write()`, `get_inline_info()`, `set_raw_inline()`, inline-data/xattr/dentry predicates, advice-bit helpers) centralize when inode metadata must be dirtied or marked for auto recovery.
- Device/zoned/discard helpers include `f2fs_is_multi_device()`, `f2fs_bdev_index()`, `f2fs_hw_support_discard()`, `f2fs_realtime_discard_enable()`, `f2fs_dev_is_readonly()`, `f2fs_is_sequential_zone_area()`, and `f2fs_allow_multi_device_dio()`.
- Compression helpers gate behavior under `CONFIG_F2FS_FS_COMPRESSION`: `set_compress_context()`, `f2fs_disable_compressed_file()`, `f2fs_may_compress()`, and `f2fs_i_compr_blocks_update()`.

## Cross-File API Surface

The bottom half of the header declares internal F2FS APIs by implementation file:

- `file.c`: sync, truncate, getattr/setattr, hole punching, shutdown, extent precache, fileattr, ioctl, project quota transfer, and pinned-file control.
- `inode.c`: inode flag setup, inode checksum verification/set, iget retry, NAT shrinking, inode update/write/evict, donate-inode removal, and failed-inode cleanup.
- `namei.c` and `dir.c`: extension-list updates, parent lookup, tmpfile creation, encrypted/casefolded filename setup/free, dentry lookup/fill/add/delete, parent metadata, link creation, and empty-dir checks.
- `super.c`: inode dirty/synced transitions, quota setup/sync/off, max file blocks, error recording, superblock commit, sync_fs, and checkpoint sanity.
- `node.c`: nid range/free-memory checks, fsync-node tracking, NAT/node info lookup, dnode traversal, node folio allocation/get/write/move, node-page writeback, free-nid allocation lifecycle, xattr recovery, NAT flush, and node-manager cache lifecycle.
- `segment.c`: SSR decisions, atomic write commit/abort, foreground/background balance, flush/discard thread control, invalidation, prefree transitions, no-checkpoint unusable blocks, curseg save/restore, section allocation, trim, summary/meta/node writes, block replacement/allocation, device state, block writeback waits, SIT flush, write pointer repair, segment-manager lifecycle, and rw-hint mapping.
- `checkpoint.c`: operation locking, checkpoint stop/flush/thread lifecycle, meta folio operations, block-address validation, meta readahead/sync, inode-entry/orphan tracking, dirty inode/page management, checkpoint read/write/issue, and checkpoint cache lifecycle.
- `data.c`: bioset/cache lifecycle, write merge IO, read/write bio submission, target device lookup, data block address updates/reservation, data folio lookup/allocation, map/fiemap, encryption, inplace/outplace write decisions, page invalidation/release, overwrite checks, post-read processing, and iomap ops.
- `gc.c` and `recovery.c`: GC thread/manager/victim selection/range/resize and fsync-data roll-forward recovery.
- `debug.c`, `inline.c`, `shrinker.c`, `extent_cache.c`, `sysfs.c`, `verity.c`, and `compress.c`: optional statistics, inline inode/dir/data handling, cache reclaim, extent cache operations, sysfs registration, fs-verity ops, and compression read/write/cache routines.

## Control Flow and State Transitions

Mount-time initialization builds `struct f2fs_sb_info`, fills `mount_opt`, validates feature bits, initializes locks/counters, creates node/segment/checkpoint/compression/stat caches, and registers sysfs/shrinker state. The rest of the filesystem retrieves shared state through `F2FS_SB()` and related accessors.

The normal write path passes through inode/page helpers into `f2fs_map_blocks()` or dnode traversal, reserves blocks via `inc_valid_block_count()` or `inc_valid_node_count()`, updates node block addresses through `dnode_of_data`, and eventually submits a `f2fs_io_info` through merged or page bio functions. Segment allocation and SIT/NAT updates are delegated to `segment.c`/`node.c`, but this header defines the state that both sides must mutate consistently.

Checkpoint flow is coordinated through `cp_global_sem`, `cp_rwsem`, `node_write`, `node_change`, checkpoint flags, dirty inode/page lists, orphan/ino-entry lists, NAT/SIT journals, and summary helpers. `__get_cp_reason()`, `enabled_nat_bits()`, bitmap pointer helpers, and cp-pack address helpers all encode details required by checkpoint write and recovery code.

Recovery flow reuses fsync node lists, NAT/node summary helpers, orphan inode APIs, inline/xattr recovery prototypes, and roll-forward checkpoint flags. The `FI_AUTO_RECOVER` and dirty inode helpers decide whether inode metadata must be persisted or can be skipped safely.

GC and discard flow use idle-time predicates (`f2fs_update_time()`, `f2fs_time_over()`, `is_inflight_io()`, `is_idle()`), segment manager state, victim/ATGC structures, pinned-file controls, and discard command queues. Zoned-device helpers can force discard or constrain allocation/write-pointer behavior.

Compression flow is cluster based. `set_compress_context()` initializes per-inode compression from mount options and marks persistent inode flags. Read IO uses `decompress_io_ctx` refcounts and remaining-page accounting before decompression and optional verity. Write IO uses `compress_ctx` and `compress_io_ctx` to batch cluster pages and update compressed-block accounting.

## State and Persistence Behavior

This header is tightly coupled to persistent F2FS layout. `block_t`, `nid_t`, on-disk feature bits, inode flags, inline flags, checkpoint flags, NAT/SIT bitmap offsets, summary journal accessors, inode extra-attribute sizing, and address-array calculations all depend on on-disk structures from F2FS format headers.

Persistent state changes are deliberately funneled through dirtying helpers:

- Inode size, block count, link count, depth, xattr nid, parent ino, inline flags, ACL mode, compression context, advice bits, and relevant FI flags call `f2fs_mark_inode_dirty_sync()` when they alter disk-visible state.
- Superblock/checkpoint consistency issues set flags such as `SBI_NEED_FSCK` or checkpoint error flags, causing later mount/fsck/readonly behavior to change.
- Valid block/node counters are updated under `stat_lock`, paired with quota claim/release calls, and mirrored in percpu counters used by sync and space accounting.
- Checkpoint pack selection alternates between pack 1 and pack 2; NAT/SIT bitmap pointer logic changes when large NAT bitmap or checkpoint payload features are active.
- No-checkpoint mode affects available block calculations through `SBI_CP_DISABLED` and `unusable_block_count`.

The most important persistence invariant is that in-memory counters, quota reservations, node/SIT/NAT metadata, and inode dirty flags must agree before checkpoint writes make the state durable. Several helpers mark `SBI_NEED_FSCK` instead of silently continuing when a counter underflow or invalid block condition is detected.

## Dependencies

The header depends on Linux kernel VFS/MM/block primitives (`struct inode`, `super_block`, `folio`, `address_space`, `bio`, `block_device`, writeback control, quota, rwsem, radix tree, rbtree, percpu counters, workqueues, kobjects, wait queues, completions, refcounts, CRC32, scheduler accounting, and memory allocation APIs).

Feature-specific dependencies include fscrypt, fsverity, Unicode casefolding, quotas, zoned block devices, compression backends, iostat, debug stats, lockdep, task delay accounting, and F2FS fault injection/check-fs config options.

It also depends on F2FS on-disk format definitions available elsewhere in the same source tree or included kernel headers: `struct f2fs_super_block`, `struct f2fs_checkpoint`, `struct f2fs_inode`, `struct f2fs_node`, `struct f2fs_summary_block`, `struct f2fs_journal`, `struct f2fs_dir_entry`, constants such as `F2FS_BLKSIZE`, `NEW_ADDR`, `NULL_ADDR`, `COMPRESS_ADDR`, `CP_*_FLAG`, and layout sizes like `DEF_ADDRS_PER_INODE`.

## Integration Points

`f2fs.h` is the integration point for almost every file under `fs/f2fs`. Implementation files include it to share the same `f2fs_sb_info`/`f2fs_inode_info` layout, lock wrappers, dirtying rules, feature predicates, accounting helpers, and prototypes. The declared file operations, inode operations, address-space operations, fs-verity operations, iomap ops, and slab caches connect F2FS internals to the VFS and block layer.

External integration is through kernel subsystems rather than userspace APIs: VFS inode/file/dentry operations, block bio submission and discard/flush support, quota accounting, fscrypt/fsverity post-read processing, sysfs/proc/debug stats, shrinker reclaim, workqueues, and zoned-device write constraints.

## Risks and Edge Cases

- Counter consistency is fragile. `total_valid_block_count`, `total_valid_node_count`, `current_reserved_blocks`, inode `i_blocks`, quota reservations, and percpu counters must remain paired across success and failure paths. The header contains explicit underflow checks that mark `SBI_NEED_FSCK`.
- Inline helpers encode on-disk layout arithmetic. Changes to inline xattr sizing, extra inode attributes, compression cluster size, or address-array offsets can corrupt data if not kept synchronized with the F2FS disk format.
- Lock ordering is broad and cross-file: checkpoint semaphores, node locks, curseg locks, inode semaphores, GC semaphores, quota semaphores, and IO locks are all shared here. The unfair rwsem and trace wrappers are intended to avoid priority inversions but add configuration-dependent behavior.
- Page/folio private data multiplexes pointer and bitfield layouts. Any caller that treats `folio->private` as a pointer without checking the low-bit convention can misinterpret F2FS state.
- Compression, encryption, and verity combine on post-read paths. `f2fs_post_read_required()` and `decompress_io_ctx` lifetime rules must be respected to avoid unlocking pages before verification/decompression completes or freeing compressed pages still attached to bios.
- Zoned and multi-device behavior changes discard, readonly, DIO, and sequential-zone checks. Block addresses must be translated against per-device ranges before zone checks.
- Fault injection alters allocation and accounting paths. Tests that enable it must verify release paths, not only success paths.
- Several helpers are no-ops when config options are disabled. Callers must be valid in both feature-enabled and feature-disabled builds.

## Test Signals

Useful validation signals for changes touching this header include:

- Kernel build coverage across F2FS configs: base F2FS, `CONFIG_F2FS_FS_COMPRESSION`, `CONFIG_FS_ENCRYPTION`, `CONFIG_FS_VERITY`, `CONFIG_QUOTA`, `CONFIG_BLK_DEV_ZONED`, `CONFIG_F2FS_STAT_FS`, `CONFIG_F2FS_FAULT_INJECTION`, and `CONFIG_F2FS_CHECK_FS`.
- fstests coverage for F2FS mount/remount, fsync/roll-forward recovery, checkpoint disable/enable, orphan inode recovery, inline data/dentry/xattr, compression, encryption, verity, quota, project quota, atomic write/COW, truncate/hole-punch, fiemap/bmap, GC, fstrim/discard, and multi-device or zoned-device scenarios.
- Runtime checks for absence of `SBI_NEED_FSCK`, checkpoint error flags, block/node counter underflows, quota leaks, dirty inode/list leaks, and page-private misuse warnings.
- Fault-injection runs targeting allocation, block reservation, checkpoint, discard, read/write IO, lock timeout, and consistency faults.
- Debug/stat signals from `/sys/fs/f2fs/*`, F2FS stat output, iostat counters, GC/discard/flush queue counts, compression saved-block counters, and checkpoint latency stats.
- Recovery tests that power-fail after inode size/block/link changes, NAT/SIT journal updates, compressed cluster writes, inline-data conversion, and atomic write commit/abort.
