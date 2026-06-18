# sources/distributed-fs/ceph-client/fs/f2fs/xattr.h

## Purpose
`xattr.h` defines the F2FS on-disk extended attribute format, namespace indexes, layout and alignment helpers, capacity calculations, and public xattr/security function declarations. It is the contract shared by `xattr.c`, encryption, verity, ACL, and inode metadata code.

## Important APIs, Types, And Macros
The core on-disk structures are `struct f2fs_xattr_header` and `struct f2fs_xattr_entry`. The header carries magic, refcount, and reserved words. Each entry stores namespace index, name length, value size, then inline name and value bytes. Namespace constants include user, POSIX ACL access/default, trusted, Lustre, security, advise, encryption, and verity. Special names include `system.advise`, encryption context name `c`, and verity name `v`.

Layout macros include `XATTR_HDR`, `XATTR_ENTRY`, `XATTR_FIRST_ENTRY`, `XATTR_ALIGN`, `ENTRY_SIZE`, `XATTR_NEXT_ENTRY`, `IS_XATTR_LAST_ENTRY`, and `list_for_each_xattr`. Capacity macros include `VALID_XATTR_BLOCK_SIZE`, `XATTR_PADDING_SIZE`, `XATTR_SIZE`, `MIN_OFFSET`, `MAX_VALUE_LEN`, `MIN_INLINE_XATTR_SIZE`, `MAX_INLINE_XATTR_SIZE`, and `DEFAULT_XATTR_SLAB_SIZE`.

## Control Flow
This header has no executable control flow, but its iterator and sizing macros define how `xattr.c` walks and mutates xattr tables. `list_for_each_xattr` starts after the header and advances by aligned entry size until a zero dword terminator. `XATTR_SIZE()` composes the optional external xattr block size with the inode's inline xattr size, and `MIN_OFFSET()` defines the upper bound used for free-space checks.

## State And Persistence Behavior
The documented on-disk layout places the xattr header, variable entries, free space, and node footer in a combined logical xattr area. F2FS uses inline xattr space plus at most one xattr block. The macros encode the persistence contract that entries are packed, 4-byte aligned, and terminated by zero. `MAX_VALUE_LEN()` bounds a single xattr value by the total usable xattr area minus header and entry overhead.

## Dependencies And Integration Points
The header depends on Linux xattr declarations and F2FS inode/layout constants such as `node_footer`, `DEF_ADDRS_PER_INODE`, extra-attr sizes, inline reserved sizes, and inline dentry sizes. It declares `f2fs_xattr_handlers`, `f2fs_setxattr()`, `f2fs_getxattr()`, `f2fs_listxattr()`, xattr cache init/destroy, and optional `f2fs_init_security()` stubs depending on Kconfig.

## Risks
Because the file defines raw on-disk parsing macros, changes can break compatibility or cause memory-safety bugs in xattr walking. The `IS_XATTR_LAST_ENTRY()` zero-dword test assumes enough bounds checking by callers before dereference. Capacity macros must remain consistent with inode layout changes, flexible inline xattr support, compression/encryption feature growth, and node footer size.

## Test Signals
Test signals include build coverage with and without `CONFIG_F2FS_FS_XATTR` and `CONFIG_F2FS_FS_SECURITY`, xattr boundary tests around inline size and maximum value length, ACL/security/verity/encryption xattr integration, and corrupted xattr images that exercise caller-side bounds checks.
