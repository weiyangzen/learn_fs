# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-inode-write.h

## Purpose
Declares AFR inode write-side FOP entry points for data, metadata, xattr, allocation, and fsync operations.

## Important APIs, types, and functions
Exports `afr_writev()`, `afr_truncate()`, `afr_ftruncate()`, `afr_setattr()`, `afr_fsetattr()`, `afr_setxattr()`, `afr_fsetxattr()`, `afr_removexattr()`, `afr_fremovexattr()`, `afr_discard()`, `afr_fallocate()`, `afr_zerofill()`, `afr_xattrop()`, `afr_fxattrop()`, and `afr_fsync()`.

## Control flow
These declarations are the fops-table contract. Implementations convert each call into an AFR data or metadata transaction with operation-specific wind/unwind callbacks and lock ranges.

## State and persistence behavior
The header has no direct state. The declared operations mutate child brick contents, metadata, xattrs, and AFR changelog state through the implementation.

## Dependencies and integration points
Depends on Gluster types for vectors, iobrefs, inode attributes, xattrop flags, fds, locs, dicts, and call frames. It is tightly coupled to AFR transaction and inode context internals.

## Risks and test signals
Prototype drift and missing fops registration are the header-level risks. Build and ABI checks plus integration tests for every exported write operation are the key signals.
