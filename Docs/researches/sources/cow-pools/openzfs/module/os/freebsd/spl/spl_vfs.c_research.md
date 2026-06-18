# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_vfs.c

## Scope

FreeBSD VFS compatibility helpers for OpenZFS. It manages mount options, snapshot mounting, and asynchronous vnode release.

## Main Interfaces

- `vfs_setmntopt()` allocates and appends a `struct vfsopt` to `mnt_opt`.
- `vfs_clearmntopt()` deletes a named mount option.
- `vfs_optionisset()` queries `mnt_optnew`.
- `mount_snapshot()` mounts a ZFS snapshot filesystem on a synthetic `.zfs/snapshot/<name>` vnode.
- `vn_rele_async()` releases a vnode immediately when safe, or dispatches `vrele()` to a taskq when the last reference would trigger inactive processing.

## State And Control Flow

`mount_snapshot()` validates filesystem type/path lengths, resolves the VFS type, checks that the covered vnode is a directory and not already mounted, marks `VI_MOUNT`, allocates a new mount using parent credentials, sets `from`, read-only, nosuid, and ignored mount flags, then calls `VFS_MOUNT()`. On success it installs the mount under the covered vnode, adds it to `mountlist`, signals a mount event, and returns the snapshot root vnode. On mount failure it clears `VI_MOUNT`, ends the sequence counter write, releases the vnode, frees mount options, and destroys the mount.

## Dependencies

Uses FreeBSD mount/vnode internals, mount option lists, `VFS_MOUNT`, `VFS_ROOT`, namecache purge when enabled, `taskq_dispatch()`, and vnode reference counts.

## Correctness Notes

Snapshot mounts deliberately use parent mount credentials so ordinary users cannot unmount the automounted snapshot. The covered vnode is carefully transitioned through `VI_MOUNT`, `vn_seqc_write_begin/end`, and mount-list insertion. `vn_rele_async()` is a deadlock-avoidance helper: it avoids re-entering filesystem inactive paths synchronously when releasing the final vnode reference.
