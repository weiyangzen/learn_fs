# sources/distributed-fs/ceph-client/fs/ext2/xattr_user.c

## Purpose

`fs/ext2/xattr_user.c` implements ext2 `user.*` xattr namespace handling. It gates user attributes on the `XATTR_USER` mount option and delegates actual storage to the generic ext2 xattr block implementation.

## Important APIs, types, and functions

- `ext2_xattr_user_list()` returns whether `test_opt(dentry->d_sb, XATTR_USER)` is enabled.
- `ext2_xattr_user_get()` rejects access with `-EOPNOTSUPP` when the mount option is disabled, otherwise calls `ext2_xattr_get()` with `EXT2_XATTR_INDEX_USER`.
- `ext2_xattr_user_set()` applies the same mount-option gate before calling `ext2_xattr_set()`.
- `ext2_xattr_user_handler` publishes `XATTR_USER_PREFIX`, list, get, and set callbacks.

## Control flow

VFS dispatch for `user.*` names reaches this handler. The list/get/set paths check the current superblock mount option. If enabled, they pass through to generic xattr code, including create/replace/remove flag handling and EA block allocation.

## State and persistence behavior

User attributes persist in external EA blocks under `EXT2_XATTR_INDEX_USER`. The mount option only controls exposure and mutation; existing on-disk user attributes can remain present while inaccessible if the filesystem is mounted with `nouser_xattr`.

## Dependencies and integration points

This file depends on ext2 mount-option state from `super.c`, VFS xattr handler dispatch, and generic ext2 xattr storage. `ext2_show_options()` reports `user_xattr` or `nouser_xattr` based on defaults and parsed options.

## Risks and edge cases

Behavior differs between "attribute absent" and "namespace disabled." Callers should see `-EOPNOTSUPP` when the namespace is disabled, not `-ENODATA`. Remounting with option changes can alter accessibility without changing on-disk content.

## Test signals

Mount with `user_xattr` and `nouser_xattr`, verify set/get/list behavior and error codes, remount toggling the option with existing attributes, and combine user xattrs with quota and ENOSPC injection to cover delegated storage paths.
