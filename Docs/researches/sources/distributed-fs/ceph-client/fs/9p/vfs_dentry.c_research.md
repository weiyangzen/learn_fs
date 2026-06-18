<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_dentry.c -->
# sources/distributed-fs/ceph-client/fs/9p/vfs_dentry.c

## Purpose
`vfs_dentry.c` implements 9p dentry operations, including fid cleanup, cached dentry invalidation, attribute revalidation, and rename unalias locking.

## Important APIs, types, and functions
It defines `v9fs_cached_dentry_operations` and `v9fs_dentry_operations`. Internal functions include `v9fs_cached_dentry_delete`, `v9fs_dentry_release`, `__v9fs_lookup_revalidate`, `v9fs_lookup_revalidate`, and unalias lock/unlock helpers.

## Control flow
Negative cached dentries are discarded. On release, the dentry fid hlist is moved under d_lock and all fids are put. Revalidation refreshes inode attributes when `V9FS_INO_INVALID_ATTR` is set, using dotl or legacy refresh paths, and invalidates the dentry if the server reports ENOENT or type change.

## State and persistence
State is dentry-associated fid lists and inode cache-validity flags. No local persistent data is stored.

## Dependencies and integration points
It depends on VFS dentry operations, fid lookup, inode refresh helpers, and session `rename_sem`.

## Risks and test signals
Risks include fid leaks, RCU lookup limitations, stale positive dentries, and revalidation racing with remove/rename. Test signals include dcache-heavy lookup, negative entries, remote deletion, type changes, rename aliasing, and unmount cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_dentry.c -->
