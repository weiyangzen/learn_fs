# sources/distributed-fs/ceph-client/fs/jfs/jfs_discard.h

## Purpose
Declares JFS discard and FITRIM interfaces.

## Important APIs, types, and functions
Forward declares `struct fstrim_range` and exports `jfs_issue_discard()` and `jfs_ioc_trim()`.

## Control flow
`ioctl.c` calls `jfs_ioc_trim()` for FITRIM; dmap free code calls `jfs_issue_discard()` for online discard.

## State and persistence behavior
No state; exposes functions that issue block-device discard while preserving allocation semantics.

## Dependencies and integration points
Connects JFS ioctl and dmap code.

## Risks and test signals
Build discard-enabled paths and verify callers include the right prototypes.
