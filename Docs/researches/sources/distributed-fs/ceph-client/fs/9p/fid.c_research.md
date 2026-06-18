<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/fid.c -->
# sources/distributed-fs/ceph-client/fs/9p/fid.c

## Purpose
`fid.c` manages 9p fid lookup, attachment, cloning, and association with dentries and inodes. Fids are the active protocol handles used by VFS operations.

## Important APIs, types, and functions
Exports include `v9fs_fid_add`, `v9fs_open_fid_add`, `v9fs_fid_find_inode`, and `v9fs_fid_lookup`. Internals include `v9fs_fid_find`, `v9fs_fid_lookup_with_uid`, `build_path_from_dentry`, and `v9fs_is_writeable`.

## Control flow
Lookup first searches dentry fid lists, then open inode fid lists. On miss it tries the parent fid, otherwise attaches a root fid for the selected user and walks from root in `P9_MAXWELEM` batches. It holds `rename_sem` while using dentry names to prevent path changes during multi-component walks.

## State and persistence
Fids are cached in `dentry->d_fsdata` and `inode->i_private` hlist heads. They are runtime protocol references and are clunked when dentries/files/inodes release them.

## Dependencies and integration points
It depends on p9 client attach/walk/reference counting, current fsuid, session access modes, dentry locking, inode locking, and the session `rename_sem`.

## Risks and test signals
Risks include fid leaks, stale fids after unlink/rename, race windows around d_unhashed, incorrect access mode user selection, and path walk under concurrent rename. Test signals include multi-user access modes, rename storms, open-file writeback fid reuse, root attach failures, and deep path walks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/fid.c -->
