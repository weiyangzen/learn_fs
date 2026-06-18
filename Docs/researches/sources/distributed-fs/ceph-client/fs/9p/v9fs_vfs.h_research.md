<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/v9fs_vfs.h -->
# sources/distributed-fs/ceph-client/fs/9p/v9fs_vfs.h

## Purpose
`v9fs_vfs.h` declares the shared VFS operation tables and helper functions used across 9p source files.

## Important APIs, types, and functions
It declares inode/file/dentry/super operation objects, `v9fs_fs_type`, `v9fs_req_ops`, inode allocation and stat conversion helpers, dotl helpers, option parsing/showing, and inline helpers converting inode/dentry/superblock to session state.

## Control flow
No standalone flow. It enables cross-file calls between legacy and dotl implementations, superblock setup, file operations, and address-space operations.

## State and persistence
The header owns no state but exposes operation tables that drive VFS dispatch.

## Dependencies and integration points
It integrates 9p with Linux VFS, netfs, p9 client, xattr/ACL, and filesystem registration.

## Risks and test signals
Risks include signature drift as VFS APIs change and mismatched operation tables across protocol variants. Test signals are full 9p compile coverage and mount/open/stat/create tests for legacy, 9P2000.u, and 9P2000.L.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/v9fs_vfs.h -->
