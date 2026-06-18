# sources/distributed-fs/ceph-client/fs/coda/coda_linux.h

## Purpose
`coda_linux.h` is the main Linux-kernel-facing Coda header, declaring operation tables, shared VFS operation functions, helper conversions, cnode accessors, and inode flagging.

## Important APIs, Types, And Functions
It declares Coda inode, dentry, address-space, file, directory, and ioctl operations; shared functions such as `coda_open()`, `coda_release()`, `coda_permission()`, `coda_revalidate_inode()`, `coda_getattr()`, and `coda_setattr()`; helper functions from `coda_linux.c`; and inline accessors `ITOC()`, `coda_i2f()`, `coda_i2s()`, and `coda_flag_inode()`.

## Control Flow
The only executable logic is inline object conversion and flag setting. `coda_flag_inode()` locks the cnode and ORs an invalidation flag without dropping the inode.

## State, Persistence, And Dependencies
State is in `struct coda_inode_info` embedded in VFS inodes. The header depends on VFS, memory, wait, and Coda inode private definitions.

## Integration Points
Nearly every Coda source file includes this header to wire VFS methods to Coda/Venus helpers and to access per-inode fid/flag state.

## Risks
Inline accessors assume the inode really belongs to Coda. Misusing `coda_i2s()` inherits the static-buffer caveat of `coda_f2s()`. Flagging does not perform cache eviction by itself; revalidation paths must consume the flags.

## Test Signals
Build coverage, lockdep around `coda_flag_inode()`, and broad VFS operation tests validate the header contract.
