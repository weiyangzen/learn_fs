# sources/distributed-fs/ceph-client/fs/hfsplus/xattr_user.c

Purpose: this file provides the HFS+ `user.*` xattr namespace handler.

Important APIs and functions: `hfsplus_user_getxattr()` and `hfsplus_user_setxattr()` are thin wrappers around `hfsplus_getxattr()` and `hfsplus_setxattr()` with `XATTR_USER_PREFIX`. `hfsplus_xattr_user_handler` registers the prefix and callbacks with the VFS.

Control flow: VFS xattr operations enter this handler with a suffix such as `comment`. The common helper builds `user.comment`, performs HFS+ validation and B-tree/catalog work, and returns the resulting byte count or errno.

State and persistence: local state is absent. Persistent state is the HFS+ attribute record plus catalog flags maintained by `xattr.c`.

Dependencies and integration: it depends on `hfsplus_fs.h`, `xattr.h`, NLS sizing, and Linux xattr namespace constants. It is part of `hfsplus_xattr_handlers[]`, so superblock xattr support must include the common handler table.

Risks: this layer performs no policy checks; mount options or VFS-level user xattr restrictions must be enforced elsewhere if present. Buffer sizing and unsupported non-inline HFS+ attribute formats are inherited from `xattr.c`.

Test signals: set/get/list/remove ordinary `user.*` attributes, test zero-length values, `XATTR_CREATE` and `XATTR_REPLACE`, removal by setting a `NULL` value through VFS, absent attributes returning `-ENODATA`, and behavior on resource-fork inodes returning `-EOPNOTSUPP`.
