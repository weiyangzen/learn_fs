# sources/distributed-fs/ceph-client/fs/ext2/xattr_trusted.c

## Purpose

`fs/ext2/xattr_trusted.c` implements the ext2 `trusted.*` xattr namespace. Trusted attributes are intended for privileged kernel/user-space consumers and are visible in listxattr only to callers with `CAP_SYS_ADMIN`.

## Important APIs, types, and functions

- `ext2_xattr_trusted_list()` returns true only for `capable(CAP_SYS_ADMIN)`.
- `ext2_xattr_trusted_get()` and `ext2_xattr_trusted_set()` call the generic ext2 xattr engine with `EXT2_XATTR_INDEX_TRUSTED`.
- `ext2_xattr_trusted_handler` publishes `XATTR_TRUSTED_PREFIX`, list, get, and set callbacks.

## Control flow

VFS dispatch selects this handler for names under `trusted.`. Listing checks capability through the `.list` callback. Get and set operations delegate to `ext2_xattr_get()` and `ext2_xattr_set()`, which perform storage validation, locking, allocation, and persistence.

## State and persistence behavior

Trusted attributes persist in ext2 external EA blocks under the trusted namespace index. No independent state is stored in this file. Visibility during list operations is dynamic and depends on caller credentials, not on-disk bits.

## Dependencies and integration points

The file depends on Linux capabilities, VFS xattr handlers, `xattr.h` namespace definitions, and the generic ext2 xattr storage implementation. Its handler is included in `ext2_xattr_handlers` when ext2 xattrs are enabled.

## Risks and edge cases

Capability gating only affects listing here; get/set permission enforcement also involves VFS xattr policy. Tests must distinguish "not listed" from "not present." Storage errors and malformed EA blocks propagate from `xattr.c`.

## Test signals

List `trusted.*` attributes as privileged and unprivileged callers, get/set/remove trusted attributes, verify persistence after remount, and exercise malformed EA block handling through this namespace.
