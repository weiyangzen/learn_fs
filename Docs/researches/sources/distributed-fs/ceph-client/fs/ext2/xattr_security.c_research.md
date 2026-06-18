# sources/distributed-fs/ceph-client/fs/ext2/xattr_security.c

## Purpose

`fs/ext2/xattr_security.c` implements the `security.*` xattr namespace for ext2 and integrates inode creation with Linux Security Module label initialization. It is compiled when ext2 security xattrs are enabled.

## Important APIs, types, and functions

- `ext2_xattr_security_get()` calls `ext2_xattr_get()` with `EXT2_XATTR_INDEX_SECURITY`.
- `ext2_xattr_security_set()` calls `ext2_xattr_set()` with the security namespace index.
- `ext2_initxattrs()` iterates an LSM-provided `struct xattr` array and writes each label into ext2 xattrs.
- `ext2_init_security()` calls `security_inode_init_security()` with `ext2_initxattrs()` as the filesystem writer callback.
- `ext2_xattr_security_handler` publishes the `XATTR_SECURITY_PREFIX`, get, and set callbacks to VFS xattr dispatch.

## Control flow

VFS xattr operations on `security.*` dispatch through the handler into generic ext2 xattr storage. Inode creation paths call `ext2_init_security()`, which asks the LSM to compute initial labels for the new inode and parent/name context; the callback then writes each returned label with normal ext2 xattr set semantics.

## State and persistence behavior

Security labels persist in the same external EA blocks managed by `xattr.c`, under namespace index `EXT2_XATTR_INDEX_SECURITY`. This file does not add separate state. LSM-provided labels are persisted before or during inode creation depending on the caller path.

## Dependencies and integration points

The file depends on Linux security hooks, VFS xattr handler registration, and ext2 generic xattr storage. It is referenced by `xattr.h` and included in ext2 handler arrays only under the relevant configuration.

## Risks and edge cases

Partial initialization is possible if an LSM returns multiple xattrs and a later write fails; callers must handle the returned error. Security namespace availability is build-time controlled, so images with security labels mounted on a kernel without this option cannot expose them through handlers. The handler does not perform additional permission checks itself; it relies on VFS/LSM xattr policy.

## Test signals

Create files on SELinux or another security-module-enabled system, verify labels are set at creation, get/set `security.*` labels, inject ENOSPC during label writes, and compile/mount with `CONFIG_EXT2_FS_SECURITY` disabled to confirm graceful absence.
