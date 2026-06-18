# sources/distributed-fs/ceph-client/fs/ext4/xattr_trusted.c

## Purpose

`fs/ext4/xattr_trusted.c` implements the ext4 VFS xattr handler for the `trusted.*` namespace. It maps trusted xattrs to `EXT4_XATTR_INDEX_TRUSTED` and restricts listing to administrators.

## Important APIs, Types, and Functions

The file defines `ext4_xattr_trusted_list()`, `ext4_xattr_trusted_get()`, `ext4_xattr_trusted_set()`, and exports `ext4_xattr_trusted_handler`. The handler uses `XATTR_TRUSTED_PREFIX`.

## Control Flow

`ext4_xattr_trusted_list()` returns `capable(CAP_SYS_ADMIN)`, so unprivileged callers do not see trusted names in listxattr output. Get and set calls are thin wrappers around `ext4_xattr_get()` and `ext4_xattr_set()` using `EXT4_XATTR_INDEX_TRUSTED`. The wrapper does not perform its own capability checks for get/set; VFS and xattr core policy are expected to gate access.

## State and Persistence Behavior

Trusted values persist through common ext4 xattr storage under the trusted name index. The file itself maintains no independent state.

## Dependencies and Integration Points

It depends on Linux capability checks, VFS xattr handler dispatch, and the common ext4 xattr implementation. The exported handler is wired into the handler map and list in `xattr.c`.

## Risks and Edge Cases

The namespace's security property depends on correct VFS/core checks for get and set, because only list filtering happens locally. Any change in capability semantics or namespace policy should be checked against this wrapper. Storage corruption, ENOSPC, quota, and journaling risks are delegated to `xattr.c`.

## Test Signals

Test listxattr as privileged and unprivileged callers, verify get/set/remove of trusted xattrs with appropriate privileges, and ensure common ext4 xattr errors propagate. Also verify that trusted entries are not exposed in list output without `CAP_SYS_ADMIN`.
