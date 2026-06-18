<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_super.c -->
# sources/distributed-fs/ceph-client/fs/9p/vfs_super.c

## Purpose
`vfs_super.c` implements 9p superblock setup, mount tree creation, statfs, unmount cancellation, inode dropping, writeback hooks, and fs_context lifecycle.

## Important APIs, types, and functions
Key functions are `v9fs_get_tree`, `v9fs_fill_super`, `v9fs_kill_super`, `v9fs_umount_begin`, `v9fs_statfs`, `v9fs_drop_inode`, `v9fs_write_inode`, `v9fs_write_inode_dotl`, `v9fs_init_fs_context`, and `v9fs_free_fc`. It defines `v9fs_super_ops`, `v9fs_super_ops_dotl`, and `v9fs_fs_type`.

## Control flow
Mount allocates a session, initializes it to get the root fid, gets/sets up a superblock, creates the root inode from the fid, loads ACLs, attaches the root fid to the root dentry, and returns the root. Kill super cancels/disconnects the session after VFS teardown. Fs_context init seeds default mount/client/transport options.

## State and persistence
Superblock state points to `v9fs_session_info`; BDI readahead/io_pages reflect cache mode; POSIX ACL and xattr handler state is set from protocol/config. No local persistent filesystem metadata is kept.

## Dependencies and integration points
It depends on VFS superblock/fs_context APIs, p9 session init/close, fid lookup, inode creation, netfs writeback, statfs dotl RPCs, xattr handlers, and ACL support.

## Risks and test signals
Risks include mount failure cleanup, root fid ownership, unmount while RPCs are pending, statfs fallback, and cache-mode inode dropping behavior. Test signals include successful/failed mounts, forced unmount, statfs on dotl/non-dotl servers, remount-like option display, and memory leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_super.c -->
