# sources/distributed-fs/ceph-client/fs/xfs/xfs_xattr.h

## Purpose
`xfs_xattr.h` declares the XFS xattr bridge used by VFS-facing inode code and other XFS attribute callers.

## Important APIs, types, and functions
It forward-declares `enum xfs_attr_update`, declares `xfs_attr_change`, and exposes `xfs_xattr_handlers`.

## Control flow
VFS inode setup can install `xfs_xattr_handlers`, while attr mutation code can call `xfs_attr_change` for set/create/replace/remove operations with initialized `xfs_da_args`.

## State and persistence
The header has no state. The declared implementation mutates persistent inode attribute forks and possibly log-incompat feature state.

## Dependencies and integration points
It sits between generic inode/xattr setup and `xfs_xattr.c`, avoiding direct inclusion of the full implementation.

## Risks and test signals
Risks are limited to declaration mismatch and handler registration errors. Build coverage plus VFS xattr tests exercise it.
