# sources/distributed-fs/ceph-client/fs/squashfs/super.c

## Purpose

`super.c` implements SquashFS mount, superblock validation, per-mount state initialization, VFS filesystem registration, mount option parsing, statfs, unmount cleanup, and inode slab allocation.

## Important APIs, Types, and Functions

Important functions are `squashfs_parse_param_threads_str()`, `squashfs_parse_param_threads_num()`, `squashfs_parse_param()`, `supported_squashfs_filesystem()`, `squashfs_fill_super()`, `squashfs_get_tree()`, `squashfs_reconfigure()`, `squashfs_show_options()`, `squashfs_init_fs_context()`, `squashfs_statfs()`, `squashfs_put_super()`, inode-cache init/destroy helpers, module init/exit, `squashfs_alloc_inode()`, and `squashfs_free_inode()`. Key objects are `squashfs_fs_type` and `squashfs_super_ops`.

## Control Flow

Mount creates `squashfs_sb_info`, parses options, reads the superblock through `squashfs_read_table()`, validates magic/version/compression/device size/block size/root inode/table ordering, initializes caches and optional compressed-page cache mapping, sets up decompressor streams, loads xattr/id/export/fragment indexes in reverse table order, reads the root inode, and creates the root dentry. Failure paths free every partially allocated resource.

## State and Persistence Behavior

`msblk` owns mount-wide state: read-only filesystem geometry, decompressor/thread config, caches, table indexes, panic-on-error setting, and root table starts. Reconfigure only updates the errors behavior and forces read-only. Unmount deletes caches, cache mapping host inode, decompressor streams, indexes, meta-index cache, and `s_fs_info`.

## Dependencies and Integration Points

It integrates with fs_context, block-device mounting, VFS super operations, Kconfig-selected decompressor modes, cache/table readers, id/fragment/export/xattr table loaders, and inode read code. It registers the `squashfs` filesystem type and module metadata.

## Risks and Edge Cases

Mount validation is security-critical because all later reads trust table ordering and sizes. Risks include malformed table starts, unsupported compression, page size greater than filesystem block size, bad root inode offset, optional xattrs when kernel xattr support is disabled, and cleanup after partial initialization.

## Test Signals

Mount valid/corrupt images across compression formats, thread options, xattr/export/no-fragment variants, too-new/too-old versions, block-size boundaries, truncated block devices, remount option changes, statfs output, and kmemleak/failure-injection tests.
