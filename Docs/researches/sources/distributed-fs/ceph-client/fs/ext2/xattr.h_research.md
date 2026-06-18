# sources/distributed-fs/ceph-client/fs/ext2/xattr.h

## Purpose

`fs/ext2/xattr.h` defines the ext2 on-disk extended attribute block format, namespace indexes, alignment helpers, and public xattr API declarations or stubs. It is the contract shared by ext2 xattr storage, namespace handlers, ACL/security initialization, inode teardown, symlink xattr listing, and superblock setup.

## Important APIs, types, and constants

- `EXT2_XATTR_MAGIC` identifies valid EA blocks.
- `EXT2_XATTR_REFCOUNT_MAX` caps sharing of one identical EA block.
- `EXT2_XATTR_INDEX_USER`, `EXT2_XATTR_INDEX_POSIX_ACL_ACCESS`, `EXT2_XATTR_INDEX_POSIX_ACL_DEFAULT`, `EXT2_XATTR_INDEX_TRUSTED`, `EXT2_XATTR_INDEX_LUSTRE`, and `EXT2_XATTR_INDEX_SECURITY` define on-disk namespaces.
- `struct ext2_xattr_header` stores magic, refcount, block count, aggregate hash, and reserved fields.
- `struct ext2_xattr_entry` stores name length/index, value offset, external value block field, value size, entry hash, and inline flexible name.
- `EXT2_XATTR_LEN()`, `EXT2_XATTR_NEXT()`, and `EXT2_XATTR_SIZE()` encode 4-byte alignment for entries and values.
- When `CONFIG_EXT2_FS_XATTR` is enabled, the header declares handlers, `ext2_listxattr()`, `ext2_xattr_get()`, `ext2_xattr_set()`, `ext2_xattr_delete_inode()`, cache create/destroy helpers, and `ext2_xattr_handlers`.
- When disabled, inline stubs return `-EOPNOTSUPP`, do nothing for delete/cache destroy, and set operation pointers to `NULL`.
- `ext2_init_security()` is declared or stubbed depending on `CONFIG_EXT2_FS_SECURITY`.

## Control flow

The macros are used by `xattr.c` to iterate the variable-length entry table and calculate required free space. Build-time configuration controls whether callers link to real xattr routines or no-op stubs. Inode creation paths can call `ext2_init_security()` unconditionally because the header supplies a zero-return stub when security xattrs are unavailable.

## State and persistence behavior

This header defines persistent byte layout and alignment, so changes would affect disk compatibility. It intentionally represents only one-block EA storage: `h_blocks` must be one in validation code and `e_value_block` is not implemented for external value blocks. The function stubs affect in-memory feature availability but do not change on-disk existing xattr data.

## Dependencies and integration points

It includes Linux xattr declarations, depends on `struct inode`, `struct dentry`, `struct mb_cache`, and xattr handler types, and is included by ext2 superblock, symlink, ACL, security, trusted, user, and generic xattr code.

## Risks and edge cases

Alignment macros must remain consistent with on-disk parsing. Namespace index values are persistent and cannot be renumbered. The disabled-xattr stubs should match caller expectations, especially returning `-EOPNOTSUPP` rather than `-ENODATA`. The Lustre index is defined even though this subset does not provide a handler, so list/get behavior depends on handler-map coverage.

## Test signals

Compile with xattrs enabled and disabled, security enabled and disabled, and POSIX ACL enabled/disabled. Validate macro calculations for short and long names and values, ensure disabled builds produce no xattr handlers, and mount images with existing xattr blocks to confirm layout compatibility.
