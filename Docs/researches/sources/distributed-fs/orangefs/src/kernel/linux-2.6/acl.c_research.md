## sources/distributed-fs/orangefs/src/kernel/linux-2.6/acl.c

Purpose: Implements Linux VFS POSIX ACL support for the PVFS2/OrangeFS kernel module by storing ACLs as extended attributes and integrating with inode creation, chmod, and permission checks.

Important APIs and functions: `pvfs2_get_acl` retrieves access/default ACL xattrs and decodes them with `posix_acl_from_xattr`. `pvfs2_set_acl` validates object type, updates mode bits via `posix_acl_equiv_mode`, encodes ACLs with `posix_acl_to_xattr`, and writes/removes xattrs through `pvfs2_inode_setxattr`. Xattr handlers `pvfs2_xattr_acl_access_handler` and `pvfs2_xattr_acl_default_handler` expose get/set callbacks. `pvfs2_init_acl` applies inherited default ACLs and umask during inode creation. `pvfs2_acl_chmod` updates access ACLs after chmod. `pvfs2_permission` delegates to `generic_permission` when available or uses a local DAC/ACL fallback.

Control flow: All active code is compiled only for non-2.4 kernels with generic xattr and POSIX ACL support. Get/set paths first check the mount ACL flag. Xattr setters enforce owner or `CAP_FOWNER`, decode and validate the supplied ACL, then call `pvfs2_set_acl`. Inode initialization fetches the parent default ACL, possibly stores it on new directories, masks mode bits, stores an access ACL if needed, and flushes mode changes. Permission checks invoke `pvfs2_check_acl` when the kernel's generic permission API supports ACL callbacks.

State and persistence: ACLs persist as PVFS2 extended attributes named `PVFS2_XATTR_NAME_ACL_ACCESS` and `PVFS2_XATTR_NAME_ACL_DEFAULT`. In-memory state includes inode mode changes and PVFS2 inode mode-dirty flags flushed to the server.

Dependencies and integration points: Depends on Linux POSIX ACL API variants selected by configure macros, PVFS2 xattr helpers, inode flush helpers, capability/current fsuid APIs, and kernel namespace helpers.

Risks: `pvfs2_xattr_get_acl_default` calls `pvfs2_xattr_get_acl(... ACL_TYPE_ACCESS ...)`, which appears to return the access ACL for the default ACL handler. `pvfs2_acl_chmod` has duplicated chmod/update logic across compatibility branches, risking double work. `pvfs2_set_acl` allocates a debug string before early symlink/ACL-disabled returns and can leak it. It checks `IS_ERR` after `kmalloc` instead of null. Many compile-time branches target different kernel ACL signatures, so untested configurations can rot.

Test signals: Test mount with ACLs disabled/enabled, get/set/remove access and default ACL xattrs, default ACL inheritance for files/directories, chmod ACL masking, symlink denial, owner/capability checks, generic permission integration, cross-endian xattr encoding, and every configured kernel ACL API branch.
