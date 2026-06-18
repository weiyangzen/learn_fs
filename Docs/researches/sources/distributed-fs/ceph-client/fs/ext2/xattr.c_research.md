# sources/distributed-fs/ceph-client/fs/ext2/xattr.c

## Purpose

`fs/ext2/xattr.c` implements ext2 extended attributes stored in external EA blocks referenced by `EXT2_I(inode)->i_file_acl`. It provides VFS xattr get/list/set/delete behavior, validates the ext2 EA block format, shares identical EA blocks across inodes through mbcache and on-disk refcounts, updates the ext2 compat feature bit, and frees EA blocks during inode deletion.

## Important APIs, types, and functions

- `ext2_xattr_handler_map` maps on-disk name indexes to Linux xattr handlers for `user`, POSIX ACL pseudo-handlers, `trusted`, and optional `security`.
- `ext2_xattr_handlers` is installed into `sb->s_xattr` by `super.c`.
- `ext2_xattr_get()` reads a named attribute, validates the header and each entry, searches sorted entries with `ext2_xattr_cmp_entry()`, inserts the block into mbcache, and copies or sizes the value.
- `ext2_listxattr()` and `ext2_xattr_list()` validate the block and emit visible names with prefixes only when `xattr_handler_can_list()` allows them.
- `ext2_xattr_set()` creates, replaces, or removes one attribute, using `XATTR_CREATE` and `XATTR_REPLACE` semantics, quota initialization, `xattr_sem`, sorted entry insertion/removal, value compaction, and copy-on-write when a shared block cannot be modified in place.
- `ext2_xattr_set2()` commits a prepared block by reusing an identical cached block, keeping an exclusive old block, allocating a new block, updating inode `i_file_acl`, dirtying metadata, and releasing the old block.
- `ext2_xattr_release_block()` decrements a shared block refcount or frees an exclusive EA block, synchronized against cache reuse.
- `ext2_xattr_delete_inode()` releases the inode's EA block during inode eviction after validating block range and header.
- `ext2_xattr_cache_insert()`, `ext2_xattr_cache_find()`, `ext2_xattr_cmp()`, `ext2_xattr_hash_entry()`, and `ext2_xattr_rehash()` implement deduplication by content hash plus full block comparison.
- `ext2_xattr_create_cache()` and `ext2_xattr_destroy_cache()` manage the per-superblock mbcache.

## Control flow

Get/list paths acquire `xattr_sem` for reading, read `i_file_acl` with `sb_bread()`, validate `EXT2_XATTR_MAGIC`, single-block layout, entry bounds, value offsets, and non-external values, then search or list entries. Set paths initialize quotas, acquire `xattr_sem` for writing, read the existing block if present, locate the insertion point in sorted order, compute available free space, enforce create/replace/remove rules, and either modify an exclusive uncached block under lock or clone/allocate a scratch block. The update phase rehashes the block unless empty, then `ext2_xattr_set2()` deduplicates or allocates the final block and points the inode at it.

When deleting an inode, the code uses `down_write_trylock()` because reclaim lockdep contexts are sensitive, reads the EA block if one exists, checks it is a valid data block, validates the header, releases/free-refcounts it, and clears `i_file_acl`.

## State and persistence behavior

Persistent EA state consists of an external block containing `struct ext2_xattr_header`, sorted `struct ext2_xattr_entry` records, value bytes packed from the block end, block-level hash, entry hashes, and refcount. The inode persists the EA block number in `i_file_acl`. The superblock compat feature `EXT2_FEATURE_COMPAT_EXT_ATTR` is set on first new EA block allocation through `ext2_xattr_update_super_block()`, which may upgrade the filesystem revision. In-memory state includes `xattr_sem`, mbcache entries keyed by hash/block number, and buffer-head verified/dirty state.

## Dependencies and integration points

The file integrates with ext2 block allocation/free (`ext2_new_blocks()`, `ext2_free_blocks()`), data block validation, inode dirtying, synchronous inode metadata writes, quota accounting, VFS xattr handlers, POSIX ACL handlers, security labels, mbcache, buffer-head IO, and superblock feature update helpers from `super.c`. Namespace-specific handlers in `xattr_user.c`, `xattr_trusted.c`, and `xattr_security.c` call into these generic routines.

## Risks and edge cases

EA block validation is security critical because offsets and lengths come from disk. Bad headers, value blocks, out-of-range offsets, and malformed entry chains must produce `-EIO` and mark errors rather than overrun memory. Shared-block refcounting is subtle: in-place modification is allowed only for exclusive blocks that are not concurrently being reused through mbcache. Cache hash collisions are handled by full block compare. Quota accounting must match refcount increments, decrements, allocations, and frees. Synchronous inodes require dirty buffer and inode metadata errors to be propagated carefully, including the special ENOSPC cleanup behavior.

## Test signals

Test get/list/set/remove for user/trusted/security/ACL namespaces; create vs replace flag errors; maximum name and value lengths; empty block removal; repeated identical xattr sets across many inodes to exercise shared blocks; mutation of one inode after sharing to verify copy-on-write; inode deletion freeing or decrementing EA blocks; corruption tests for header magic, refcount, offsets, padding, external value block, and bad `i_file_acl`; quota exhaustion; sync inode writeback errors; and superblock feature-bit updates on old revision filesystems.
