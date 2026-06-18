# sources/distributed-fs/ceph-client/fs/squashfs/xattr.c

## Purpose

`xattr.c` implements listing and retrieving SquashFS extended attributes for user, trusted, and security namespaces.

## Important APIs, Types, and Functions

Public objects/functions are `squashfs_listxattr()` and `squashfs_xattr_handlers`. Internal functions are `squashfs_xattr_get()`, `squashfs_xattr_handler_get()`, `squashfs_trusted_xattr_handler_list()`, and `squashfs_xattr_handler()`. It uses `struct squashfs_xattr_entry` and `struct squashfs_xattr_val`.

## Control Flow

Listxattr checks that the filesystem has xattr support, then walks the inode's xattr entries. For each entry it selects a namespace handler, optionally emits the namespace prefix and name, skips or reads the value header and value, and tracks remaining user buffer space. Getxattr walks entries until prefix/name match; for out-of-line values it follows the stored xattr pointer before reading the value.

## State and Persistence Behavior

Xattr locations/counts/sizes are cached per inode; xattr id table and xattr table start are per mount. Attribute values remain read-only metadata and are copied to user buffers on demand.

## Dependencies and Integration Points

Integrated through VFS xattr handlers installed by `super.c` and inode operation `listxattr` hooks. It depends on metadata reading and xattr ids populated by `inode.c`/`xattr_id.c`.

## Risks and Edge Cases

Buffer sizing must return `-ERANGE` without overrunning user buffers. Unknown xattr types are ignored. Trusted xattrs require `CAP_SYS_ADMIN` for listing. Out-of-line value pointers must be handled carefully to avoid reading wrong metadata.

## Test Signals

`getfattr`/`listxattr` tests for user/trusted/security namespaces, permission checks for trusted list, no-xattr images, out-of-line values, small buffers, and corrupt xattr metadata.
