<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/xattr.c -->
# sources/distributed-fs/ceph-client/fs/9p/xattr.c

## Purpose
`xattr.c` implements extended attribute get/set/list support for 9p using 9P2000.L xattrwalk and xattrcreate operations.

## Important APIs, types, and functions
Exports include `v9fs_fid_xattr_get`, `v9fs_xattr_get`, `v9fs_xattr_set`, `v9fs_fid_xattr_set`, `v9fs_listxattr`, and `v9fs_xattr_handlers`. Internal xattr handler callbacks map VFS namespaces to full xattr names.

## Control flow
Get walks to an xattr fid, handles size-only queries and range errors, reads the xattr value, then clunks the attr fid. Set clones the target fid, creates or replaces the xattr stream, writes the value, and clunks the cloned fid. Listing is implemented as xattr get with an empty name.

## State and persistence
No local xattr state is stored. Values persist on the 9p server. Handler registration is static per superblock.

## Dependencies and integration points
It depends on p9 xattr RPCs, fid cloning/lookup, iov_iter, VFS xattr handlers, and optional security namespace support.

## Risks and test signals
Risks include size overflow, partial write errors, clone/clunk error ordering, server namespace restrictions, and empty-name list semantics. Test signals include get size/value, ERANGE, set/remove/create/replace flags, listxattr, security labels, and server errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/xattr.c -->
