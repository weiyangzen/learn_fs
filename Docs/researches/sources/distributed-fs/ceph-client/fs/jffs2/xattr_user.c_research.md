# sources/distributed-fs/ceph-client/fs/jffs2/xattr_user.c

## Purpose
Registers the JFFS2 `user.*` xattr namespace handler.

## Important APIs, types, and functions
`jffs2_user_getxattr()` and `jffs2_user_setxattr()` call the common helpers with `JFFS2_XPREFIX_USER`. `jffs2_user_xattr_handler` advertises `XATTR_USER_PREFIX` plus get/set callbacks.

## Control flow
VFS user-xattr operations are thinly mapped to `do_jffs2_getxattr()` and `do_jffs2_setxattr()`.

## State and persistence behavior
No independent state. Prefix/name/value are stored by the shared JFFS2 xattr core.

## Dependencies and integration points
Depends on Linux xattr APIs, JFFS2 prefix constants, and common helper declarations.

## Risks and test signals
Test create, replace, remove, size query, `-ERANGE`, and remount persistence for `user.*`.
