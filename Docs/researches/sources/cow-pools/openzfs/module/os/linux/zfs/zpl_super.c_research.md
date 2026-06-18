# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_super.c

## Purpose
Implements Linux superblock, filesystem type, fs_context, mount/remount, statfs, sync, inode lifecycle, dentry-cache, and mount-option behavior for ZFS.

## Main APIs and Data
- Tunables `zfs_delete_inode` and `zfs_delete_dentry` control inode/dentry cache retention.
- `zpl_super_operations` provides inode allocation/destruction, dirtying, drop/evict, unmount, sync, statfs, and mount display callbacks.
- `zpl_fs_context_operations` provides option parsing, mount tree creation, reconfigure, duplicate, and free callbacks.
- `zpl_fs_type` registers the ZFS filesystem type.
- `zpl_param_spec[]` defines accepted mount options.

## Control Flow
Inode allocation delegates to `zfs_inode_alloc()` and initializes i_version. Dirty inode callback pushes Linux inode changes into ZFS system attributes. Drop inode either uses normal generic caching or immediate deletion based on tunable. Eviction truncates pages, clears inode state, and calls `zfs_inactive()`.

Unmount calls `zfs_umount()` through `put_super`; `kill_sb` performs `zfs_preumount()` then `kill_anon_super()`. Sync wraps `zfs_sync()` and contains compatibility handling for older kernels where `syncfs()` ignored `sync_fs()` errors, using `s_wb_err` or waiting for TXG sync as needed. Statfs adapts `zfs_statvfs()` and scales block/file counts for 32-bit callers.

Mount option parsing handles Linux common options, ZFS-specific temporary options, SELinux passthrough, sloppy unknown-option behavior, snapshot mountpoint data, and legacy strings produced by mount tools. For kernels with forbidden sb flags in monolithic parsing, `zpl_parse_monolithic()` splits options itself so ZFS can still see options like `atime`, `dev`, `exec`, and `suid`.

`zpl_get_tree()` holds the named objset, uses `sget()` with `zpl_test_super()` to avoid duplicate mounts, rechecks the objset under ZFS enter locks, calls `zfs_domount()` for new superblocks, and rejects incompatible ro/rw multimounts for non-snapshots. Remount delegates to `zfs_remount()` and transfers ownership of parsed `vfs_t` options on success.

## Integration Points
This file is the kernel mount lifecycle bridge into `zfs_vfsops`, `zfs_znode`, DMU objset holding, DSL dataset long holds, Linux fs_context parsing, Linux superblock shrink/prune behavior, and mount option presentation in `/proc/self/mounts`.

## Invariants and Edge Cases
- DSL pool lock is released before `sget()` to avoid deadlocks with superblock teardown.
- Existing superblocks are revalidated against current `z_os` because rollback/unmount can race.
- Snapshot mounts are always effectively readonly and bypass one ro/rw conflict check.
- Mount options are deliberately permissive to preserve OpenZFS mount helper compatibility.
- Unknown options emit kernel notices rather than hard failure.
- `fc->fs_private` ownership transfers to `zfsvfs` on successful mount/remount.
- Dentry deletion tunable trades lookup overhead for lower inode/dbuf/ARC pinning.

## Risks and Testing Signals
Test mount/remount option compatibility across old/new kernels, duplicate mounts, rollback races, snapshot automount options, syncfs error reporting on older kernels, 32-bit statfs scaling, immediate inode/dentry deletion tunables, idmapped mount flags, and cleanup of fs_context allocation/dup/free paths.
