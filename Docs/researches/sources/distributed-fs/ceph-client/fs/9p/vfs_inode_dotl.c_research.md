<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_inode_dotl.c -->
# sources/distributed-fs/ceph-client/fs/9p/vfs_inode_dotl.c

## Purpose
`vfs_inode_dotl.c` implements 9P2000.L-specific inode operations using Linux-like protocol RPCs for open/create, mkdir, mknod, symlink, hardlink, getattr, setattr, and ACL-aware creation.

## Important APIs, types, and functions
Important functions are `v9fs_inode_from_fid_dotl`, `v9fs_open_to_dotl_flags`, `v9fs_vfs_setattr_dotl`, `v9fs_stat2inode_dotl`, `v9fs_refresh_inode_dotl`, and dotl operation helpers for atomic open, mkdir, mknod, symlink, link, and getattr. It exports inode operation tables for directories, files, and symlinks.

## Control flow
Dotl inode lookup uses `p9_client_getattr_dotl` and qid plus generation for inode matching. Creation paths compute inherited gid and ACL-adjusted mode, issue protocol-native create/mkdir/mknod, walk back to an unopened fid, instantiate the inode, and set inherited ACLs. Setattr maps Linux `ATTR_*` bits to dotl valid flags, flushes dirty data, calls `p9_client_setattr`, resizes netfs/fscache state, and updates ACLs on chmod.

## State and persistence
Runtime state includes inode generation, qid, cached ACLs, netfs size state, and fid associations. Persistent data and metadata live on the 9p server.

## Dependencies and integration points
It depends on dotl p9 client RPCs, shared legacy lookup/remove/rename helpers, ACL/xattr code, fid management, FS-Cache, and VFS inode operation tables.

## Risks and test signals
Risks include ACL/mode ordering, fid ownership after atomic open, generation-based inode matching, partial stat masks, setattr time precision, and cache size synchronization. Test signals include 9P2000.L create/open, ACL inheritance, symlink/readlink, hardlink, mknod, setattr truncate/chmod/chown, and metadata caching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_inode_dotl.c -->
