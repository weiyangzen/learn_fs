# sources/distributed-fs/ceph-client/fs/ext4/xattr_user.c

## Purpose

`fs/ext4/xattr_user.c` implements the ext4 VFS xattr handler for the `user.*` namespace. It gates user xattrs on the ext4 `XATTR_USER` mount option and maps them to `EXT4_XATTR_INDEX_USER`.

## Important APIs, Types, and Functions

The file defines `ext4_xattr_user_list()`, `ext4_xattr_user_get()`, `ext4_xattr_user_set()`, and exports `ext4_xattr_user_handler`. The handler uses `XATTR_USER_PREFIX`.

## Control Flow

All operations first check the mount option. Listing returns true only when `test_opt(dentry->d_sb, XATTR_USER)` succeeds. Get and set return `-EOPNOTSUPP` when the option is disabled; otherwise they call `ext4_xattr_get()` or `ext4_xattr_set()` with the user namespace index.

## State and Persistence Behavior

User xattrs persist under the ext4 user name index and are stored by the common xattr engine in inode body, EA block, or EA inode form. This wrapper keeps no additional state.

## Dependencies and Integration Points

The file depends on ext4 mount-option handling, VFS xattr dispatch, and the common ext4 xattr implementation. Its exported handler is part of `ext4_xattr_handlers` and `ext4_xattr_handler_map`, affecting both VFS operations and list filtering.

## Risks and Edge Cases

The main risk is mount-option policy: user xattrs must not be accessible when `XATTR_USER` is disabled. The wrapper ignores idmap details, which is normal for raw xattr data but should stay aligned with VFS expectations. Size, quota, corruption, and journal behavior are delegated to `xattr.c`.

## Test Signals

Mount with and without user xattrs enabled. Verify `user.*` list/get/set/remove behavior, `-EOPNOTSUPP` propagation when disabled, correct persistence across remount, and fallback behavior for inode-body, EA block, and large-value storage.
