# sources/distributed-fs/ceph-client/fs/ext4/xattr.h

## Purpose

`fs/ext4/xattr.h` defines the ext4 extended attribute on-disk format, namespace indexes, storage layout helpers, in-memory helper structs, lock helpers, and exported function prototypes used by ext4 xattr, ACL, security, and inode-management code.

## Important APIs, Types, and Functions

The key on-disk constants are `EXT4_XATTR_MAGIC`, `EXT4_XATTR_REFCOUNT_MAX`, and the namespace indexes for user, POSIX ACL access/default, trusted, Lustre, security, system, richacl, encryption, and Hurd xattrs. `struct ext4_xattr_header` is the external block header with magic, refcount, block count, block hash, checksum, and reserved fields. `struct ext4_xattr_ibody_header` marks in-inode xattr storage. `struct ext4_xattr_entry` stores the name length/index, value offset, optional EA inode number, value size, entry hash, and inline name.

The layout macros `EXT4_XATTR_LEN()`, `EXT4_XATTR_NEXT()`, and `EXT4_XATTR_SIZE()` implement 4-byte padding. `IHDR()`, `ITAIL()`, and `IFIRST()` locate the inode-body xattr area from a raw ext4 inode. `BHDR()`, `BFIRST()`, `ENTRY()`, and `IS_LAST_ENTRY()` do the same for external xattr blocks. `EXT4_INODE_HAS_XATTR_SPACE()` checks whether the inode has enough extra-inode room for an ibody xattr header, one entry, padding, and data.

The in-memory control structs are `ext4_xattr_info`, `ext4_xattr_search`, `ext4_xattr_ibody_find`, and `ext4_xattr_inode_array`. Exported APIs include get/list/set paths, journal credit estimation, inode deletion cleanup, extra-isize expansion, EA inode eviction, ibody find/get/set, mbcache creation/destruction, inode xattr validation, optional security initialization, optional lockdep class setup, and quota usage accounting.

## Control Flow

This header does not implement full control flow, but it defines how callers traverse storage: start with a header, use `IFIRST()` or `BFIRST()` to obtain the first entry, iterate with `EXT4_XATTR_NEXT()`, and stop when `IS_LAST_ENTRY()` sees the null terminator. Writers use `ext4_write_lock_xattr()`, `ext4_write_trylock_xattr()`, and `ext4_write_unlock_xattr()` to protect xattr mutation and to set `EXT4_STATE_NO_EXPAND` while the xattr semaphore is held.

## State and Persistence Behavior

The structs in this file are the persistent ABI for ext4 xattrs. Entry value bytes may be inline in the inode or external block, or may be referenced by `e_value_inum` when large EA inode storage is enabled. `EXT4_XATTR_SIZE_MAX` is intentionally larger than the current user-visible xattr size limit to support consistency checks without overflow-prone `INT_MAX` arithmetic. `EXT4_XATTR_MIN_LARGE_EA_SIZE()` defines when using an external inode can be worthwhile by reserving room in an EA block for at least one entry and terminator.

## Dependencies and Integration Points

The header includes `<linux/xattr.h>` and is consumed by ext4 xattr namespace handlers, ext4 ACL code, security initialization, inode expansion code, and eviction paths. Its locking helpers depend on `EXT4_I(inode)->xattr_sem` and inode state flags from `ext4.h`. Security initialization is compiled to `ext4_init_security()` only when `CONFIG_EXT4_FS_SECURITY` is enabled; otherwise it is an inline no-op.

## Risks and Edge Cases

The layout macros are pointer-arithmetic heavy and assume validated input. Callers must validate entry bounds before trusting `EXT4_XATTR_NEXT()` or value offsets. `EXT4_STATE_NO_EXPAND` is intentionally overloaded: it can mean inline xattrs/data are too full to expand, or that xattr write locking is preventing recursive expansion. Callers using the lock helpers must preserve and restore the prior state flag correctly.

## Test Signals

Tests should cover xattr layout iteration, padding, maximum name and value boundaries, in-inode capacity checks for different inode sizes and `i_extra_isize`, conditional compilation of security and lockdep paths, and correct save/restore behavior of `EXT4_STATE_NO_EXPAND` around xattr writes.
