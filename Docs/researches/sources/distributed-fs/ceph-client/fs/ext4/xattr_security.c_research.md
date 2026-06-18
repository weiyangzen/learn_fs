# sources/distributed-fs/ceph-client/fs/ext4/xattr_security.c

## Purpose

`fs/ext4/xattr_security.c` implements the ext4 VFS xattr handler for `security.*` labels and provides the inode-creation hook that initializes security xattrs from Linux Security Modules.

## Important APIs, Types, and Functions

The file defines `ext4_xattr_security_get()`, `ext4_xattr_security_set()`, `ext4_initxattrs()`, `ext4_init_security()`, and exports `ext4_xattr_security_handler`. The handler uses `XATTR_SECURITY_PREFIX` and delegates storage to `EXT4_XATTR_INDEX_SECURITY`.

## Control Flow

Normal get/set calls are direct wrappers around `ext4_xattr_get()` and `ext4_xattr_set()` with the security namespace index. During inode creation, `ext4_init_security()` calls `security_inode_init_security()` and passes `ext4_initxattrs()` as the callback. The callback iterates the LSM-provided `struct xattr` array and writes each label into the new inode using `ext4_xattr_set_handle()` with the caller's existing journal handle and `XATTR_CREATE`. Iteration stops on the first negative error.

## State and Persistence Behavior

Security labels persist as ext4 xattrs with `EXT4_XATTR_INDEX_SECURITY`. Because initialization uses the transaction handle supplied by the creator, initial labels are committed atomically with inode creation metadata. Storage location and large-value behavior are delegated to the common xattr layer.

## Dependencies and Integration Points

This file depends on `<linux/security.h>` and LSM xattr initialization semantics. It integrates with ext4 inode creation through the `ext4_init_security()` prototype in `xattr.h`, which compiles only under `CONFIG_EXT4_FS_SECURITY`. It also integrates with the common xattr engine, jbd2 handles, and VFS xattr dispatch.

## Risks and Edge Cases

Failure to set any one initial label aborts the callback and returns the error to inode creation. Journal credit sizing must account for all security xattrs that can be emitted by active LSMs. Because `ext4_initxattrs()` uses `XATTR_CREATE`, pre-existing labels on a reused or unexpected inode state should fail rather than replace. Runtime security get/set authorization is expected to be enforced above or around VFS xattr dispatch; this wrapper only selects storage.

## Test Signals

Tests should create files under SELinux, Smack, AppArmor, or another label-producing LSM and verify that labels are initialized and journaled with the inode. Exercise `security.*` get/set/remove through VFS APIs, forced ENOSPC or journal-credit failures during label creation, and propagation of errors from `ext4_xattr_set_handle()`.
