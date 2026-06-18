# sources/distributed-fs/ceph-client/fs/afs/dir_silly.c

Purpose: `dir_silly.c` implements AFS silly rename for unlinking busy files on a stateless server. The file is renamed to a hidden `.__afsXXXX` name and removed when the last reference is dropped.

Important APIs and functions: public entry points are `afs_sillyrename()` and `afs_silly_iput()`. Internal helpers include `afs_do_silly_rename()`, `afs_silly_rename_success()`, `afs_silly_rename_edit_dir()`, `afs_do_silly_unlink()`, `afs_silly_unlink_success()`, and `afs_silly_unlink_edit_dir()`.

Control flow: `afs_sillyrename()` rejects already-renamed dentries, finds an unused hidden name, holds the inode, issues a rename operation, marks the vnode/dentry on success, and moves the dentry. On uncertain interruption it drops dentries for later lookup. `afs_silly_iput()` handles alias races with `d_alloc_parallel()`, marks the lock state deleted to avoid release complaints, and issues the deferred remove-file RPC.

State and persistence: parent directories cache `silly_key` for later unlink. Dentries carry `DCACHE_NFSFS_RENAMED`; vnodes carry `AFS_VNODE_SILLY_DELETED` and possibly `AFS_VNODE_LOCK_DELETED`. Directory cache edits replace the original name with the hidden one, then remove the hidden one after final unlink if data versions still line up.

Dependencies and integration points: invoked by unlink and rename replacement paths in `dir.c`; depends on `fs_operation.c`, `afs_fs_rename()`, `afs_fs_remove_file()`, YFS variants, dcache aliasing, `rmdir_lock`, directory edit helpers, vnode status commit, and flock tracing.

Risks: interrupted or failed cleanup can leave hidden files until later recovery. Alias transfer in `afs_silly_iput()` is subtle. Static hidden-name generation relies on lookup collision handling. Lock-state deletion must wake/quiet waiters correctly.

Test signals: unlink open files, duplicate sillyrename rejection, hidden-name collisions, interrupted rename, last-close cleanup, alias race, conflict-triggered status fetch, and `silly_key` lifetime.
