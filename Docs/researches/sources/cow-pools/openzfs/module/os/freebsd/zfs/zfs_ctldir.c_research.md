# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_ctldir.c

## Scope

FreeBSD implementation of the synthetic `.zfs` control directory and `.zfs/snapshot` automount behavior. It builds virtual vnodes for `.zfs`, `snapshot`, and snapshot mountpoints using an in-file synthetic filesystem layer.

## Main Interfaces

- Synthetic vnode helpers: `sfs_vgetx()`, `sfs_vnode_get()`, `sfs_vnode_insert()`, `sfs_readdir_common()`, and reclaim helpers.
- Control directory lifecycle: `zfsctl_create()`, `zfsctl_destroy()`, `zfsctl_root()`, `zfsctl_is_node()`.
- VOP vectors: `zfsctl_ops_root`, `zfsctl_ops_snapdir`, and `zfsctl_ops_snapshot`.
- Snapshot lookup/mount: `zfsctl_snapdir_lookup()`, `zfsctl_snapshot_lookup()`, `zfsctl_snapshot_zname()`, `zfsctl_mounted_here()`.
- Snapshot listing/attrs: `zfsctl_snapdir_readdir()` and `zfsctl_snapdir_getattr()`.
- Unmount/lookup helpers: `zfsctl_lookup_objset()`, `zfsctl_umount_snapshots()`, `zfsctl_snapshot_unmount()`.

## State And Control Flow

`sfs_node_t` stores synthetic names, parent IDs, and IDs. The vnode hash key uses both parent and child id to avoid clashes between synthetic/root/snapshot id domains. `zfsctl_create()` allocates `.zfs` and `snapshot` nodes and copies root creation time for `.zfs` attributes.

Root lookup accepts `.`, `..`, and `snapshot`; root readdir emits `.`, `..`, and `snapshot`. Common vnode methods reject writes, report virtual directory attributes, produce short ZFS fids, expose pathconf ACL behavior, and return a trivial read/execute NFSv4 ACL.

Snapshot directory lookup validates a snapshot name, obtains or creates a synthetic snapshot vnode, waits/retries if another mount is in progress, constructs `<dataset>@<snap>` and mountpoint strings, calls `mount_snapshot()`, and returns the mounted snapshot root. On success it sets the mounted snapshot zfsvfs parent to the head filesystem and clears `VV_ROOT` so NFS traversal behaves as expected.

Snapshot readdir walks `dmu_snapshot_list_next()` with the directory offset as a cookie. Snapshot vnode reclaim frees its synthetic node; inactive recycles it. Unmount helpers locate mounted snapshot vnodes and call `dounmount()`.

## Dependencies

Uses FreeBSD vnode hash, VOP vectors, mount and namei APIs, ZFS dataset/snapshot listing, `mount_snapshot()` from `spl_vfs.c`, ZFS enter/exit, and NFS-oriented fid/path resolution behavior.

## Correctness Notes

The snapshot vnode can be uncovered, mounting, covered, or recently unmounted; lookup loops carefully to avoid racing automount and unmount. `zfsctl_umount_snapshots()` loops until transient uncovered states settle. The file explicitly notes root readdir’s small-buffer limitation: it expects enough room for its fixed entries or returns according to FreeBSD directory-read conventions.
