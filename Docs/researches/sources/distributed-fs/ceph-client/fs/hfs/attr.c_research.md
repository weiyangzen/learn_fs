# sources/distributed-fs/ceph-client/fs/hfs/attr.c

## Purpose
`attr.c` exposes classic HFS Finder metadata fields, file type and creator code, through Linux xattr handlers named `hfs.type` and `hfs.creator`.

## Important APIs, Types, And Functions
`enum hfs_xattr_type` distinguishes `HFS_TYPE` and `HFS_CREATOR`. `__hfs_setxattr` updates the catalog record's `UsrWds.fdType` or `UsrWds.fdCreator`. `__hfs_getxattr` retrieves the same four-byte fields. `hfs_xattr_get` and `hfs_xattr_set` adapt these helpers to the Linux xattr handler interface. `hfs_xattr_handlers` exports both handlers.

## Control Flow
Set rejects non-regular files and resource-fork inodes, initializes a catalog B-tree search, finds the inode catalog record by `HFS_I(inode)->cat_key`, reads the catalog file record, validates that the supplied value is exactly four bytes, copies the new Finder field, and writes the modified record back to the B-tree node. Get returns length four for size probes, or reads the catalog record and copies the requested four-byte field when the caller provided enough space.

## State And Persistence
The persistent state is the HFS catalog file record, specifically Finder user words inside `struct hfs_cat_file`. There is no separate xattr fork; Linux xattr calls are translated into catalog metadata updates.

## Dependencies And Integration Points
This file depends on HFS catalog B-tree search (`hfs_find_init`, `hfs_brec_find`, `hfs_bnode_read`, `hfs_bnode_write`), inode helpers, and the VFS xattr handler interface. It is linked into `hfs.o` through the HFS Makefile.

## Risks And Test Signals
Risks include exposing these attributes on unsupported inode types, accepting non-four-byte values, catalog search failures, and writeback not marking B-tree pages dirty. Signals include xattr get/set tests for `hfs.type` and `hfs.creator`, resource-fork rejection, catalog consistency after remount, and Finder metadata round trips.
