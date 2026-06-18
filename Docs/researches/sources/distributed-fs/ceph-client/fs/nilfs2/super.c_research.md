# sources/distributed-fs/ceph-client/fs/nilfs2/super.c

## Purpose

`super.c` implements NILFS2 module initialization, superblock lifecycle, mount/remount parsing, checkpoint and snapshot attachment, superblock commit/cleanup, resize, statfs, freeze/unfreeze, inode slab allocation, and filesystem type registration. It is the top-level integration layer between NILFS2 internals and the VFS mount API.

## Important APIs, Types, and Functions

Global caches are `nilfs_inode_cachep`, `nilfs_transaction_cachep`, `nilfs_segbuf_cachep`, and `nilfs_btree_path_cache`. Exported functions include `__nilfs_msg()`, `__nilfs_error()`, `nilfs_alloc_inode()`, `nilfs_set_log_cursor()`, `nilfs_prepare_super()`, `nilfs_commit_super()`, `nilfs_cleanup_super()`, `nilfs_resize_fs()`, `nilfs_attach_checkpoint()`, `nilfs_checkpoint_is_mounted()`, `nilfs_read_super_block()`, `nilfs_store_magic()`, and `nilfs_check_feature_compatibility()`.

VFS operations are collected in `nilfs_sops`; filesystem context parsing uses `nilfs_parse_param()`, `nilfs_get_tree()`, `nilfs_reconfigure()`, `nilfs_free_fc()`, and `nilfs_init_fs_context()`. Mount options include barrier/nobarrier, checkpoint snapshot `cp=`, error mode, order mode, norecovery, and discard/nodiscard.

## Control Flow

Module init creates slabs, initializes sysfs support, and registers `nilfs_fs_type`. Mount setup allocates a `the_nilfs`, initializes it, copies parsed options, sets super operations/export operations, loads on-disk NILFS state, attaches the latest checkpoint root, attaches the log writer for read-write mounts, creates the root dentry, and marks the superblock dirty/unclean for read-write operation.

`nilfs_get_tree()` supports shared superblocks and snapshot mounts. A `cp=` mount must be read-only and attaches a snapshot root after verifying the checkpoint is a snapshot. Existing device mounts can be reused or reconfigured when the current tree is not busy.

Superblock commit flow prepares a valid primary/secondary superblock pair, optionally flips the active copy, sets log cursor fields, recalculates CRC, writes with optional barrier/FUA, falls back to the secondary on primary write failure, and updates protected sequence state. Cleanup marks the filesystem valid/clean again when unmounting or remounting read-only.

Resize locks segment construction, resizes the sufile segment array, constructs a segment to persist metadata changes, moves the secondary superblock, updates device size and segment count in both superblocks, commits both, and only then expands the allocation range to include newly available segments.

## State and Persistence Behavior

Persistent state includes superblock clean/error flags, mount counts/times, write times, free block count, last segment sequence, last partial segment, last checkpoint, device size, segment count, and checksum. The file also manages volatile mount options, roots, sysfs groups, slab caches, and `sb->s_fs_info`.

`__nilfs_error()` marks `NILFS_ERROR_FS` on disk for metadata incoherence, optionally remounts read-only or panics depending on mount options. Freeze writes a clean superblock; unfreeze marks it unclean again for writable operation.

## Dependencies and Integration Points

`super.c` integrates Linux module, fs_context, block device, VFS super operations, seq_file option display, sysfs, NILFS metadata files (`cpfile`, `sufile`, `ifile`, `dat`), segment writer, recovery/load code through `load_nilfs()`, snapshot roots, btree/path caches, and export operations.

## Risks and Edge Cases

Superblock dual-copy handling is delicate: fallback, flipping, CRC calculation, and secondary relocation must maintain at least one valid copy. Resize ordering protects the secondary superblock from allocation until migration completes. Remount from read-only to read-write must reject unsupported read-only-compatible features. Snapshot mounts must avoid writable access. Error handling paths in `nilfs_fill_super()` and module cache creation must release partially initialized metadata inodes, sysfs groups, and caches.

## Test Signals

Tests should cover clean and unclean read-write mounts, read-only snapshot mounts, invalid `cp=` combinations, remount RO/RW, unsupported feature bits, superblock CRC failures and fallback, error modes (`continue`, `remount-ro`, `panic` where feasible), freeze/unfreeze, statfs counts, resize shrink/expand including secondary superblock movement, module init/exit, and fault injection through mount failure stages.
