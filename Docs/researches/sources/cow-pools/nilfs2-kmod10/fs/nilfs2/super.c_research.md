# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/super.c

## Summary
Implements NILFS2 module registration, superblock operations, mount/remount logic, checkpoint/snapshot attachment, filesystem resize, superblock commit/cleanup, error handling, statfs, and slab cache lifecycle.

## Main Responsibilities
- Registers the `nilfs2` filesystem type and module init/exit hooks.
- Owns slab caches for NILFS inodes, transaction contexts, segment buffers, and btree paths.
- Provides VFS `super_operations`.
- Parses fs_context mount parameters.
- Loads the current checkpoint or a read-only snapshot checkpoint.
- Attaches/detaches the log writer for read-write mounts.
- Commits primary and secondary superblocks with CRCs and barrier-aware sync.
- Handles remount read-only/read-write transitions.
- Resizes the filesystem and relocates the secondary superblock.
- Reports filesystem stats and mount options.

## Key APIs
- `__nilfs_msg()`, `__nilfs_error()`.
- `nilfs_alloc_inode()`.
- `nilfs_set_log_cursor()`.
- `nilfs_prepare_super()`, `nilfs_commit_super()`, `nilfs_cleanup_super()`.
- `nilfs_resize_fs()`.
- `nilfs_attach_checkpoint()`.
- `nilfs_checkpoint_is_mounted()`.
- `nilfs_read_super_block()`.
- `nilfs_store_magic()`.
- `nilfs_check_feature_compatibility()`.

## Important Behavior
Superblock writes calculate CRC over the valid superblock byte range after clearing `s_sum`. `nilfs_sync_super()` writes the active superblock with optional preflush/FUA and can fall back to the spare superblock on primary `-EIO`.

`nilfs_prepare_super()` repairs an invalid copy from the valid one when possible and optionally swaps the active superblock. `nilfs_sb_will_flip()` in `the_nilfs.h` controls periodic flipping to spread superblock writes.

Mount parsing supports `errors=`, `barrier`/`nobarrier`, `cp=`, `order=relaxed|strict`, `norecovery`, and `discard`/`nodiscard`. Snapshot mounts require `cp=` plus read-only mode.

`nilfs_fill_super()` allocates and initializes `the_nilfs`, loads metadata and recovery state, creates the sysfs device group, attaches the current checkpoint, starts the log writer for writable mounts, builds the root dentry, and marks the filesystem mounted/dirty on disk.

`nilfs_get_tree()` supports shared superblocks for the current tree and additional snapshot roots. It rejects incompatible read/write reuse and attaches checkpoint roots under `mounted_snapshots`.

Resize first adjusts sufile segment count under segment-constructor exclusion, constructs a checkpoint, moves the secondary superblock, updates on-disk size and segment count, commits both superblocks, then widens the allocatable segment range.

## State and Synchronization
`ns_sem` protects shared superblock fields and on-disk superblock preparation/commit. `ns_segctor_sem` excludes resize, checkpoint attachment metadata reads, and writer operations. Snapshot mounting is serialized by `ns_snapshot_mount_mutex`.

## Risks
Mount/remount behavior depends on preserving `SB_RDONLY` and recovery state carefully. Superblock fallback and dual-copy synchronization are subtle, especially during resize. Snapshot mounts share the block superblock but attach different checkpoint roots, so dentry/root lifetime checks are important.
