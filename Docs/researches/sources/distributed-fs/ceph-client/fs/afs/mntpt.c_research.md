<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/mntpt.c -->
# sources/distributed-fs/ceph-client/fs/afs/mntpt.c

## Purpose
Implements AFS mountpoint and autocell automount behavior. AFS mountpoints are special symlinks or pseudo-directory entries that trigger creation of a submount for another cell/volume.

## Important APIs, Types, And Functions
Provides `afs_mntpt_file_operations`, `afs_mntpt_inode_operations`, `afs_autocell_inode_operations`, `afs_d_automount()`, and `afs_mntpt_kill_timer()`. Internal helpers reject normal lookup/open on mountpoints, parse mountpoint parameters with `afs_mntpt_set_params()`, and create submounts with `afs_mntpt_do_automount()`.

## Control Flow
When VFS automounts a mountpoint dentry, `afs_d_automount()` creates a submount context, inherits the source net namespace, derives cell and volume from either pseudo-directory name or symlink contents, mounts through `fc_mount()`, then puts the mount on an expiry list. A delayed work item periodically calls `mark_mounts_for_expiry()`.

## State And Persistence
Maintains a global `afs_vfsmounts` expiry list and delayed expiry work on `afs_wq`. Mountpoint interpretation updates a temporary `afs_fs_context`; the mounted volume/cell state is owned by the resulting superblock.

## Dependencies And Integration Points
Uses fs_context submount APIs, VFS automount expiry, AFS cell lookup, symlink reading via `afs_get_link()`, and mount parsing in `super.c`.

## Risks And Edge Cases
Bad symlink content, overlong cell names, backup-to-backup mount crossing, pseudo-directory names beginning with `.`, and net namespace replacement are sensitive. Expiry work must be cancelled only after the mount list is empty.

## Test Signals
Automount regular AFS mountpoint symlinks, autocell pseudo-directories, forced RW (`.` prefix), backup volume rejection, malformed symlink content, and mount expiry after inactivity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/mntpt.c -->
