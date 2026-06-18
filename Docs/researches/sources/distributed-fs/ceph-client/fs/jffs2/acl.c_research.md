# sources/distributed-fs/ceph-client/fs/jffs2/acl.c

## Purpose
`acl.c` implements JFFS2 POSIX ACL support on top of JFFS2 xattrs. It converts between Linux `struct posix_acl` objects and the compact on-flash JFFS2 ACL format, retrieves and stores ACL xattrs, updates inode mode bits for access ACL changes, and stages inherited ACLs during inode creation.

## Important APIs, types, and functions
External functions are `jffs2_get_acl()`, `jffs2_set_acl()`, `jffs2_init_acl_pre()`, and `jffs2_init_acl_post()`. Internal conversion helpers are `jffs2_acl_size()`, `jffs2_acl_count()`, `jffs2_acl_from_medium()`, `jffs2_acl_to_medium()`, and `__jffs2_set_acl()`. Persistent payload types are declared in `acl.h`: `jffs2_acl_header`, `jffs2_acl_entry_short`, and `jffs2_acl_entry`. Xattr prefixes are `JFFS2_XPREFIX_ACL_ACCESS` and `JFFS2_XPREFIX_ACL_DEFAULT`.

## Control flow
`jffs2_get_acl()` rejects RCU lookup with `-ECHILD`, maps ACL type to the JFFS2 xattr prefix, queries the xattr size with `do_jffs2_getxattr()`, allocates a buffer if present, reads the value, and converts it with `jffs2_acl_from_medium()`. `-ENODATA` and `-ENOSYS` map to no ACL.

`jffs2_set_acl()` maps the ACL type. For access ACLs, it calls `posix_acl_update_mode()` to compute the inode mode implied by the ACL; if the mode changes it updates mode and ctime through `jffs2_do_setattr()`. For default ACLs, it rejects setting an ACL on non-directories with `-EACCES`. It then serializes or removes the xattr via `__jffs2_set_acl()` and updates the inode ACL cache on success.

`jffs2_init_acl_pre()` is called during inode creation before the inode has been fully persisted. It calls `posix_acl_create()` using the parent directory and proposed mode, caches inherited default/access ACLs on the new inode, and adjusts the mode through the `i_mode` pointer. `jffs2_init_acl_post()` later writes cached default/access ACLs to xattrs after the inode exists.

## State and persistence behavior
On-flash ACL data starts with `JFFS2_ACL_VERSION`, then stores the first four canonical ACL entry classes in short form and user/group named entries in long form with IDs. Conversion uses JFFS2 endian helpers (`je16`, `je32`) and maps IDs through `init_user_ns`. A null ACL removes the xattr; `-ENODATA` from deletion is normalized to success. ACL caches (`i_acl`, `i_default_acl`) are populated during creation and after successful set operations.

## Dependencies and integration points
This file depends on POSIX ACL helpers, JFFS2 xattr get/set, JFFS2 setattr, MTD/JFFS2 endian types, inode ACL caching, and the VFS ACL operation hooks declared in `acl.h`. It only builds when `CONFIG_JFFS2_FS_POSIX_ACL` is enabled, which itself depends on JFFS2 xattrs.

## Risks and edge cases
Conversion is format-sensitive. Malformed sizes, unknown versions, invalid tags, trailing bytes, and UID/GID entries that overrun the buffer all return `-EINVAL`. The count calculation assumes the fixed ordering/short-entry convention for the first four entries. `jffs2_acl_to_medium()` allocates based on `acl->a_count`; unexpected tags fail and free the buffer. Access ACL updates must keep mode bits and ACL xattr synchronized, or permission checks can diverge. RCU get is unsupported and must return `-ECHILD` for VFS retry.

## Test signals
Test get/set/remove access and default ACLs, inherited ACLs at inode creation, non-directory default ACL rejection, ACL mode-bit updates and ctime changes, malformed ACL blobs with bad version/size/tag/trailing data, named user/group ID round trips, no-xattr cases returning null ACL, xattr set/delete failures, cache updates, and builds with POSIX ACL disabled.
