<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/xattr.h -->
# sources/distributed-fs/ceph-client/fs/9p/xattr.h

## Purpose
`xattr.h` declares 9p xattr helpers and the xattr handler table used by dotl superblocks and ACL support.

## Important APIs, types, and functions
It declares `v9fs_xattr_handlers`, `v9fs_fid_xattr_get`, `v9fs_xattr_get`, `v9fs_fid_xattr_set`, `v9fs_xattr_set`, and `v9fs_listxattr`.

## Control flow
No executable flow. It provides cross-file linkage for inode, ACL, and superblock code.

## State and persistence
No state is owned by the header.

## Dependencies and integration points
It integrates `xattr.c` with ACL routines and dotl inode operation tables.

## Risks and test signals
Risks are declaration drift and missing handler availability when xattrs are disabled by mount flags. Test signals include build coverage and xattr-enabled/disabled mounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/xattr.h -->
