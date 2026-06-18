# sources/distributed-fs/ceph-client/fs/jffs2/super.c

## Purpose

`super.c` is the Linux module and superblock integration layer for JFFS2. It registers the filesystem, handles fs_context parsing and mount setup on MTD devices, wires VFS super/export operations, allocates/frees JFFS2 inodes from a slab cache, synchronizes write buffers, and tears down filesystem state on unmount/module exit.

## Important APIs, Types, And Functions

Important functions include `jffs2_alloc_inode()`, `jffs2_free_inode()`, `jffs2_i_init_once()`, `jffs2_show_options()`, `jffs2_sync_fs()`, NFS export helpers (`jffs2_nfs_get_inode()`, `jffs2_fh_to_dentry()`, `jffs2_fh_to_parent()`, `jffs2_get_parent()`), mount-option parsing (`jffs2_parse_param()`, `jffs2_update_mount_opts()`, `jffs2_reconfigure()`), `jffs2_fill_super()`, `jffs2_get_tree()`, `jffs2_init_fs_context()`, `jffs2_put_super()`, `jffs2_kill_sb()`, `init_jffs2_fs()`, and `exit_jffs2_fs()`.

Key operation tables are `jffs2_super_operations`, `jffs2_export_ops`, `jffs2_context_ops`, and `jffs2_fs_type`.

## Control Flow

Module initialization creates the inode slab cache, initializes compressors and JFFS2 slab caches, then registers the filesystem. Mounting allocates a `struct jffs2_sb_info` in `jffs2_init_fs_context()`, parses `compr=` and `rp_size=` options, and calls `get_tree_mtd()` with `jffs2_fill_super()`. `jffs2_fill_super()` binds the MTD device and superblock, validates reserved-pool size, initializes locks and wait queues, sets VFS operation tables and flags, then calls `jffs2_do_fill_super()`.

Sync and unmount paths flush write-buffered data. `jffs2_sync_fs()` cancels delayed write-buffer work when configured, takes `alloc_sem`, and pads/flushes the write buffer. `jffs2_put_super()` flushes again, exits summary support, frees inode caches/raw refs/block arrays/flash resources/inocache lists/xattrs, syncs MTD, and returns. `jffs2_kill_sb()` stops the GC thread for writable mounts before killing the MTD superblock and freeing `c`.

## State And Persistence Behavior

This file initializes persistent-device-facing state but mostly manages volatile VFS/module resources. It sets `SB_NOATIME`, optional `SB_POSIXACL`, xattr handlers, export operations, and mount options stored in `c->mount_opts`. Sync/unmount forces pending write-buffer data to flash, making it persistence-critical even though it does not encode raw nodes itself.

## Dependencies And Integration Points

It integrates Linux module infrastructure, fs_context, MTD superblock helpers, VFS super/export APIs, JFFS2 compressors, xattrs, ACLs, summary cleanup, flash cleanup, and GC thread lifecycle. It also exposes mount options used by allocation/compression code (`rp_size`, compressor override).

## Risks And Edge Cases

Mount option `rp_size` is checked for multiplication overflow and device-size overflow. Remount updates options under `alloc_sem` after syncing. NFS export ignores inode generation because JFFS2 expects not to reuse inode numbers before flash rewrite, which is a semantic tradeoff. Teardown order matters: pending write-buffer work must not race with freed buffers, raw refs must be freed after caches are no longer active, and RCU-delayed inode frees are flushed before destroying the inode cache on module exit.

## Test Signals

Tests should cover mount/unmount, remount with compression and reserve-pool updates, invalid `rp_size`, sync flushing on write-buffered media, module init failure unwinding at each stage, NFS filehandle lookup, xattr/ACL superblock flags, and unmount while delayed writeback work is pending.
