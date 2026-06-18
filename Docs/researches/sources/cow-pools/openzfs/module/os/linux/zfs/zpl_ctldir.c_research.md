# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_ctldir.c

## Purpose
Provides Linux VFS operation tables and callbacks for ZFS control directories: `.zfs`, `.zfs/snapshot`, and `.zfs/shares`. These entries expose snapshots and share definitions through normal directory lookup/readdir while bridging to `zfsctl_*` internals.

## Main APIs and Data
- `zpl_fops_root` / `zpl_ops_root` implement `.zfs`.
- `zpl_fops_snapdir` / `zpl_ops_snapdir` implement `.zfs/snapshot`.
- `zpl_fops_shares` / `zpl_ops_shares` implement `.zfs/shares`.
- `zpl_common_open()` rejects write opens for control directories.
- `set_snapdir_dentry_ops()` installs automount/revalidate dentry operations for snapshot dentries.

## Control Flow
The root `.zfs` directory emits `.`/`..`, `snapshot`, and `shares` unless the control directory is disabled. Lookups delegate to `zfsctl_root_lookup()` and splice the returned inode into the dentry cache.

Snapshot lookup calls `zfsctl_snapdir_lookup()`, marks filesystem transaction context, and installs `DCACHE_NEED_AUTOMOUNT` plus custom dentry ops. Automount uses `zfsctl_snapshot_mount()` and returns `NULL` so the userspace mount collision path does not double-add the vfsmount. Snapshot readdir enumerates snapshots with `dmu_snapshot_list_next()` under DSL pool config locks and emits synthetic inode numbers. Snapshot mkdir/rmdir/rename map to snapshot create, remove, and rename operations via `zfsctl_snapdir_*`.

Shares lookup and iteration delegate either to `zfsctl_shares_lookup()` or, when a real shares directory is configured, to `zfs_zget()` and `zfs_readdir()` for that object. Attribute handlers return synthetic empty-directory stats when absent or real stats for the configured shares object.

## Integration Points
This file is the Linux-facing entry point for the cross-platform ZFS control directory implementation in `zfs_ctldir`. It relies on `zpl_enter()`/`zpl_exit()`, SPL fstrans markers, ZFS credentials, DSL snapshot listing, and kernel dentry automount behavior.

## Invariants and Edge Cases
- Control directories are read-only through `open`.
- Negative snapshot dentries are not trusted because snapshots may appear later.
- Existing snapshot mountpoint dentries are kept to avoid immediate automount/unmount churn.
- Kernel-version compatibility is handled for dentry op installation and idmapped getattr/mkdir/rename signatures.
- `.zfs/shares` gracefully behaves as an empty directory when `z_shares_dir == 0`.

## Risks and Testing Signals
Test snapshot listing, lookup, creation, deletion, rename, automount from multiple namespaces, `.zfs` disabled behavior, shares directory absence/presence, and compatibility with kernels where dentry ops must be modified directly.
