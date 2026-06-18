# sources/distributed-fs/ceph-client/fs/fat/file.c

## Purpose
`file.c` provides regular-file VFS operations and common FAT ioctls, plus truncate, fallocate, getattr, setattr, fsync, and close-time flush behavior. It translates Linux file operations into FAT's limited attribute and cluster-chain model.

## Important APIs, Types, and Functions
- `fat_generic_ioctl()` dispatches attribute get/set, volume ID, and `FITRIM`.
- `fat_ioctl_set_attributes()` maps FAT attributes to Linux mode changes and enforces immutable/security checks.
- `fat_file_fsync()` syncs file data and metadata buffers, then flushes the block device.
- `fat_fallocate()` supports regular-file preallocation, with `FALLOC_FL_KEEP_SIZE` allocating clusters without growing i_size.
- `fat_truncate_blocks()` and internal `fat_free()` free cluster chains after a target offset.
- `fat_getattr()` returns FAT-specific block size, optional stable NFS inode number, and VFAT birth time.
- `fat_setattr()` handles chmod/chown-like restrictions, size changes, FAT timestamp truncation, and dirtying.

## Control Flow
Ioctls first validate userspace access and permissions, then use shared helpers. Attribute setting calls `mnt_want_write_file()`, locks the inode, sanitizes disallowed FAT bits, runs LSM `security_inode_setattr()`, calls `fat_setattr()`, sends fsnotify, and updates `S_IMMUTABLE` if configured.

Fallocate locks the inode, rejects unsupported flags and non-regular files, and either allocates additional clusters up to the requested keep-size reservation or expands the file via `fat_cont_expand()`. Truncation invalidates the cluster cache, writes the new start/EOF state before freeing tail clusters, updates timestamps and archive bit, and then frees the old chain through `fat_free_clusters()`.

## State and Persistence
This file mutates `i_mode`, FAT attribute bits, `i_start`, `i_logstart`, `i_blocks`, `mmu_private`, timestamps, and on-disk directory entries through inode writeback. Directory entry metadata is written by `fat_sync_inode()` or normal dirty inode writeback; cluster table changes are delegated to `fatent.c`. `fat_file_release()` optionally starts writeback for `flush` mounts.

## Dependencies and Integration Points
It integrates with VFS file operations, LSM hooks, fsnotify, block discard, address-space writeback in `inode.c`, FAT entry allocation/freeing, timestamp helpers, metadata-buffer helpers, and mount options in `msdos_sb_info`. Directory file operations in `dir.c` reuse `fat_generic_ioctl()` and `fat_file_fsync()`.

## Risks and Test Signals
FAT cannot represent arbitrary Unix mode changes, ownership changes, or sparse holes. `quiet` may hide permission errors for compatibility. The archive bit and read-only bit are encoded through FAT attributes, not normal Unix metadata. Tests should cover chmod/chown behavior, FAT attribute ioctls, immutable system files, truncate/grow/shrink, fallocate keep-size and eviction, fsync durability, `FITRIM`, volume ID ioctl, and `STATX_BTIME`.
