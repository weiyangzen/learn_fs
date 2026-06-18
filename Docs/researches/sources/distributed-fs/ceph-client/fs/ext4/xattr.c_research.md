# sources/distributed-fs/ceph-client/fs/ext4/xattr.c

## Purpose

`fs/ext4/xattr.c` is the core ext4 extended attribute implementation. It stores, lists, updates, shares, validates, and deletes xattrs held in three possible places: the inode body, one external EA block referenced by `EXT4_I(inode)->i_file_acl`, and, when the `ea_inode` feature is enabled, separate EA inodes for large values. The file also owns the mbcache-backed deduplication path for shared EA blocks and shared EA inodes, journal credit estimation for xattr mutations, and cleanup of EA references during inode deletion.

## Important APIs, Types, and Functions

The public entry points are `ext4_xattr_get()`, `ext4_listxattr()`, `ext4_xattr_set()`, `ext4_xattr_set_handle()`, `ext4_xattr_set_credits()`, `__ext4_xattr_set_credits()`, `ext4_xattr_ibody_find()`, `ext4_xattr_ibody_set()`, `ext4_xattr_ibody_get()`, `ext4_expand_extra_isize_ea()`, `ext4_xattr_delete_inode()`, `ext4_xattr_inode_array_free()`, `ext4_evict_ea_inode()`, `ext4_xattr_create_cache()`, `ext4_xattr_destroy_cache()`, and `ext4_get_inode_usage()`.

`ext4_xattr_handler_map` maps on-disk name indexes to VFS xattr handlers for `user`, POSIX ACLs, `trusted`, `security`, and `hurd`; `ext4_xattr_handlers` is the handler list exported to VFS inode operations. The implementation uses the on-disk structs and macros from `xattr.h`, plus `ext4_xattr_info`, `ext4_xattr_search`, `ext4_xattr_ibody_find`, and the local `ext4_xattr_block_find`.

Validation is centered on `check_xattrs()`, `ext4_xattr_check_block()`, and `__xattr_check_inode()`. Search and enumeration are handled by `xattr_find_entry()`, `ext4_xattr_list_entries()`, `ext4_xattr_ibody_list()`, and `ext4_xattr_block_list()`. Large-value EA inode support uses `ext4_xattr_inode_iget()`, `ext4_xattr_inode_get()`, `ext4_xattr_inode_lookup_create()`, `ext4_xattr_inode_create()`, `ext4_xattr_inode_write()`, `ext4_xattr_inode_update_ref()`, and `ext4_xattr_inode_dec_ref_all()`. Block sharing uses `ext4_xattr_block_cache_insert()`, `ext4_xattr_block_cache_find()`, `ext4_xattr_cmp()`, `ext4_xattr_release_block()`, `ext4_xattr_hash_entry()`, and `ext4_xattr_rehash()`.

## Control Flow

Reads take `EXT4_I(inode)->xattr_sem` for read in `ext4_xattr_get()`. They search the inode-body xattr area first via `ext4_xattr_ibody_get()` and then fall back to the external EA block via `ext4_xattr_block_get()`. Both paths validate bounds and on-disk invariants before copying data. If an entry has `e_value_inum`, the value is loaded through `ext4_xattr_inode_get()`, which igets the EA inode, checks size, reads all value blocks, validates the crc32c-derived value hash, and may insert the EA inode into the cache.

Listing follows the same two-storage order in `ext4_listxattr()`, but each entry is filtered through `ext4_xattr_prefix()` and `xattr_handler_can_list()`, so namespace-specific visibility rules apply before names are copied to the user buffer.

Writes normally enter through `ext4_xattr_set()`, which initializes quotas, computes credits, starts an `EXT4_HT_XATTR` journal handle, and calls `ext4_xattr_set_handle()`. `ext4_xattr_set_handle()` takes the xattr write lock, verifies available journal credits, reserves the raw inode for modification, finds the target entry in the inode and block areas, enforces `XATTR_CREATE`/`XATTR_REPLACE`, skips unchanged inline values, and tries to store the new value first in the inode body. On `-ENOSPC`, it tries or creates an EA block. If the value is too large and `ea_inode` is available, it retries with `i.in_inode = 1`. Successful mutation updates the superblock xattr compat feature, ctime, inode version, raw inode metadata, and marks fast commit ineligible for xattr changes.

`ext4_xattr_set_entry()` is the shared in-memory editor. It calculates old and new padded value sizes, compacts old values, inserts or removes the name entry, stores either inline value bytes or an EA inode number, updates entry hashes, and rehashes an EA block when needed. It deliberately performs failure-prone EA inode iget/refcount work before modifying the xattr entry region.

External block updates in `ext4_xattr_block_set()` choose among in-place mutation of an exclusive block, cloning a shared block, reusing an identical cached block by incrementing its refcount, or allocating a new metadata block. Replacement of a previous block releases the old block through `ext4_xattr_release_block()`, which decrements the block refcount or frees the block and decrements all referenced EA inodes.

Deletion during inode eviction is handled by `ext4_xattr_delete_inode()`. It decrements EA inode references found in the inode body, releases the external EA block, clears `i_file_acl`, marks the inode dirty, and returns any deferred EA inodes to `ext4_xattr_inode_array_free()` for `iput()`.

## State and Persistence Behavior

On disk, inode-body xattrs start at `IHDR()` after `i_extra_isize`; block xattrs start with an `ext4_xattr_header` at `i_file_acl`. Block xattr headers include magic, refcount, hash, checksum, and block count. Entry descriptors grow upward while value bytes are packed from the end of the storage region downward. EA blocks are sorted; inode-body entries are not.

Shared EA blocks persist through `h_refcount`, `h_hash`, and the inode's `i_file_acl`. Metadata checksums cover the block number and header/data with `h_checksum` zeroed for calculation. Large EA values persist in hidden regular EA inodes whose refcount is encoded in ctime plus raw i_version, whose value hash is stored in atime seconds, and whose parent/backpointer compatibility is recognized for old Lustre-style EA inodes. Quota is charged to the parent inode even when the large EA value is shared.

All persistent mutations are journaled through jbd2 handles, buffer write access calls, dirty metadata calls, inode dirtying, and metadata block allocation/free. The file takes care to handle journal restarts while decrementing EA inode refs and to zero block tails and value padding before writeback.

## Dependencies and Integration Points

This file integrates with VFS xattr handlers, POSIX ACL handler constants, jbd2/ext4 journaling, ext4 inode allocation and block mapping, quota operations, mbcache, metadata checksums, inline data, fast commit eligibility, ext4 error reporting, and lockdep. It depends on the namespace wrappers in `xattr_user.c`, `xattr_trusted.c`, `xattr_security.c`, and `xattr_hurd.c`, and on `xattr.h` for all storage layout definitions.

## Risks and Edge Cases

The highest-risk areas are corruption validation, refcount transitions, and ENOSPC paths. `check_xattrs()` defends against out-of-bounds names, overlapping values, unsupported EA inode references, invalid EA inode numbers, oversized values, and invalid checksums. Shared block races require buffer locking plus mbcache delete-or-get semantics so a block is not modified while another thread is trying to reuse it. EA inode refcounts can wrap, so `ext4_xattr_inode_update_ref()` explicitly checks zero and `U64_MAX`. Journal credit underestimation is guarded by preflight credit checks and retry-on-ENOSPC in `ext4_xattr_set()`. Hash compatibility for old signed-char name hashing is supported but warned once.

Inline data and inode expansion interact with xattr layout. `EXT4_STATE_NO_EXPAND` is set while holding the xattr write lock to avoid recursive expansion, and `ext4_expand_extra_isize_ea()` may move selected xattrs from inode body to EA block to make room for larger inode extra fields.

## Test Signals

Useful tests exercise get/list/set/remove across all namespaces, long names, create/replace flags, values that fit inode body, values that spill to EA blocks, values large enough for EA inodes, identical xattr block sharing, identical EA inode sharing, quota failures, journal credit exhaustion, nojournal mode, inline-data inodes, inode extra-isize expansion, deletion of inodes with shared EA blocks and EA inodes, and corruption injection for bad magic, bad checksum, bad value offsets, invalid `e_value_inum`, hash mismatch, and read I/O failure.
