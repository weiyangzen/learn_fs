# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_ctldir.c

## Purpose

Linux implementation of the virtual ZFS control directory, `.zfs`. It dynamically exposes `.zfs/snapshot` and `.zfs/shares`, automounts snapshots on lookup, supports optional snapshot create/remove/rename from the snapdir, handles NFS file handles for control nodes, and tracks automounted snapshots for delayed expiration.

## Snapshot Tracking

The file maintains two AVL trees:

- `zfs_snapshots_by_name`, keyed by full dataset snapshot name.
- `zfs_snapshots_by_objsetid`, keyed by `(spa, objsetid)`.

`zfs_snapentry_t` records snapshot name, mount path, spa, objset id, root dentry, delayed unmount task id, AVL nodes, refcount, mount-progress condition state, and last mount error.

Key helpers allocate/free entries, hold/release refcounts, add/remove entries to AVL trees, fill pending entries after a successful mount, find by name or objset id, and rename entries after snapshot rename. Pending entries have `se_spa == NULL` while a mount is in progress and are present only in the name tree until filled.

## Expiration And Unmount

`snapentry_expire()` is a delayed task that attempts an expire unmount, clears the task id, releases the dispatch hold, and reschedules expiration if the snapshot remained mounted. `zfsctl_snapshot_unmount_cancel()` cancels delayed unmounts and drops the held reference if cancellation wins. `zfsctl_snapshot_unmount_delay()` finds an active snapshot by objset id, cancels any previous deadline, and schedules a new one.

`zfsctl_snapshot_unmount()` waits for in-progress automounts, calls `/usr/bin/env umount -t zfs -n` with optional force, retries after `exportfs -f` on failure to clear NFS export references, maps helper failure to `EBUSY`, and releases the snapentry.

## Control Inodes

`zfsctl_inode_alloc()` creates synthetic control-directory znodes/inodes with root ownership, directory mode, control flags, no SA handle, selected inode/file ops, stable timestamps, and insertion into `z_all_znodes`. `zfsctl_inode_lookup()` first tries `ilookup()`, optionally discovers snapshot creation time from dataset metadata, and allocates on demand.

`zfsctl_create()` creates and caches the `.zfs` root inode in `zfsvfs->z_ctldir`. `zfsctl_destroy()` either removes a snapshot's snapentry on snapshot unmount or releases the cached `.zfs` root inode on filesystem unmount.

`zfsctl_root()` returns a held reference to the cached `.zfs` inode. `zfsctl_is_node()` and `zfsctl_is_snapdir()` classify synthetic control nodes.

## FID And NFS Handling

`zfsctl_fid()` generates short FIDs for `.zfs` nodes and delegates snapshot directories to `zfsctl_snapdir_fid()`. Snapshot dir FIDs are long and encode objset id plus a generation bit indicating whether the snapdir was mounted. This lets NFS `fh_to_dentry` force automount/revalidation behavior when needed.

`zfsctl_snapdir_vget()` reconstructs a snapdir inode from objset id and generation. It tries the AVL cache first, falls back to scanning snapshots for a path, triggers automount with `kern_path(... LOOKUP_FOLLOW|LOOKUP_DIRECTORY ...)`, looks up the snapdir inode, and validates the encoded mountpoint generation.

## Lookup And Snapdir Operations

`zfsctl_root_lookup()` handles lookups below `.zfs`: `..` returns the filesystem root, `snapshot` returns the snapdir inode, `shares` returns the shares inode, and disabled snapdir returns `ENOENT`.

`zfsctl_snapdir_lookup()` looks up a snapshot name in the DMU snapshot list and returns a synthetic snapdir inode keyed as `ZFSCTL_INO_SNAPDIRS - objsetid`.

When `zfs_admin_snapshot` is enabled:

- `zfsctl_snapdir_mkdir()` validates a snapshot component name, checks snapshot permission, creates a single snapshot via `dmu_objset_snapshot_one()`, then looks it up.
- `zfsctl_snapdir_remove()` resolves real case-insensitive names when needed, checks destroy permission, forcibly unmounts any active snapshot mount, then destroys the snapshot.
- `zfsctl_snapdir_rename()` validates admin mode, resolves source case when needed, builds old/new full names, checks rename policy, rejects moving across directories, renames the snapshot through DSL, and updates the snapentry name tree.

`zfsctl_shares_lookup()` delegates names below `.zfs/shares` to the configured on-disk shares directory when present.

## Automount Path

`zfsctl_snapshot_mount()` is the automount trigger. It builds full snapshot dataset name and mount path, updates the cached mountpoint when not chrooted, releases `z_teardown_lock` before blocking usermode-helper operations to avoid a documented namespace/mountinfo deadlock, coordinates concurrent mounts with a pending snapentry and condition variable, calls `/usr/bin/env mount -i -t zfs -n -o suid|nosuid`, handles busy and failure cases, follows into the mounted snapshot, marks it shrinkable, fills the snapentry with spa/objset/root dentry, schedules delayed unmount, wakes waiters, and frees local buffers.

## Initialization And Tunables

`zfsctl_init()` creates AVL trees and initializes `zfs_snapshot_lock`; `zfsctl_fini()` destroys them. Module parameters expose:

- `zfs_admin_snapshot`: allow mkdir/rmdir/mv in `.zfs/snapshot`.
- `zfs_expire_snapshot`: seconds before automatic snapshot expiration.
- `zfs_snapshot_no_setuid`: mount automounted snapshots with `nosuid`.
