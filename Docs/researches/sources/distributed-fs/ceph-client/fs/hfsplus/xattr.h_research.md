# sources/distributed-fs/ceph-client/fs/hfsplus/xattr.h

Purpose: this header is the HFS+ xattr subsystem contract. It declares the namespace-specific xattr handlers and the helper functions used by HFS+ inode/security code to set, get, list, and initialize extended attributes.

Important APIs and types: the file includes `<linux/xattr.h>` and declares `hfsplus_xattr_osx_handler`, `hfsplus_xattr_user_handler`, `hfsplus_xattr_trusted_handler`, `hfsplus_xattr_security_handler`, plus the sentinel-terminated `hfsplus_xattr_handlers[]` table consumed by superblock inode operations. The function declarations distinguish fully formed names (`__hfsplus_setxattr()`, `__hfsplus_getxattr()`) from namespace-wrapper calls (`hfsplus_setxattr()`, `hfsplus_getxattr()`) that take `prefix` and `prefixlen`.

Control flow role: there is no runtime control flow in this header, but it defines the layering used by the `.c` files. Namespace handlers in `xattr_user.c`, `xattr_trusted.c`, and `xattr_security.c` pass suffix names plus Linux namespace prefixes into `hfsplus_setxattr()`/`hfsplus_getxattr()`. Security initialization calls `hfsplus_init_security()`, which eventually uses the fully qualified setter.

State and persistence behavior: all persistence is delegated to the implementation. The declarations imply that callers provide an inode and name/value buffers; implementation code persists values into the HFS+ attributes B-tree or catalog fields and marks metadata dirty.

Dependencies and integration: consumers include HFS+ superblock setup, inode creation paths that need security labels, and VFS xattr dispatch. The header also couples handler modules to constants from `hfsplus_fs.h` and Linux namespace prefixes used by the implementation.

Risks: the split API means callers must choose the correct function. Passing an already prefixed name to the prefixing wrappers can duplicate prefixes, while passing an unprefixed name to the internal helpers can create OS X-style unnamespaced attributes. The header exposes no validation helpers, so name bounds and namespace checks are enforced only in `xattr.c`.

Test signals: build tests should verify all handler objects are defined exactly once and that superblock xattr handler registration links. Behavioral tests should cover both wrapper and internal paths, especially security initialization where names are constructed before calling `__hfsplus_setxattr()`.
