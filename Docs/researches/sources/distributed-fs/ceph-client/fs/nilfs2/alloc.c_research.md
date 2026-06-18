# sources/distributed-fs/ceph-client/fs/nilfs2/alloc.c

## Purpose

`alloc.c` implements NILFS2's persistent object allocator for metadata files such as the DAT and inode file. It manages numbered entries with on-disk group descriptors, bitmap blocks, and entry blocks, and exposes prepare/commit/abort operations so higher layers can allocate or free persistent records transactionally.

## Important APIs, Types, and Functions

Geometry helpers compute entries per group, groups per descriptor block, total group count, descriptor block offsets, bitmap block offsets, and entry block offsets. `nilfs_palloc_init_blockgroup()` initializes metadata-file allocator geometry and block-group locks. `nilfs_palloc_get_entry_block()` retrieves the entry block for an object number. `nilfs_palloc_entry_offset()` computes the byte offset of an entry in a folio.

Allocation and free APIs are `nilfs_palloc_prepare_alloc_entry()`, `nilfs_palloc_commit_alloc_entry()`, `nilfs_palloc_abort_alloc_entry()`, `nilfs_palloc_prepare_free_entry()`, `nilfs_palloc_commit_free_entry()`, `nilfs_palloc_abort_free_entry()`, and batched `nilfs_palloc_freev()`. `nilfs_palloc_count_max_entries()` estimates maximum representable entries from current descriptor blocks and growth room. Cache functions set, clear, and destroy `struct nilfs_palloc_cache`.

## Control Flow

Allocation starts from `req->pr_entry_nr`, maps it to a group and group offset, scans descriptor blocks for groups with nonzero free counts, obtains the bitmap block, atomically sets the next zero bit, decrements the group descriptor free count, and returns descriptor/bitmap buffers held in the request. Commit marks both buffers dirty and marks the metadata inode dirty; abort clears the bit, restores the descriptor free count, releases buffers, and clears request state.

Free preparation only pins descriptor and bitmap buffers. Commit clears the bitmap bit, increments the free count, warns if the entry was already free, marks buffers dirty, and marks the metadata inode dirty. `nilfs_palloc_freev()` batches entries by group, clears bits, detects entry blocks that become empty and deletes them, updates group descriptors, and deletes the bitmap block when an entire group becomes free.

## State and Persistence Behavior

Persistent state lives in metadata file blocks: group descriptors contain `pg_nfrees`, bitmap blocks contain allocation bits, and entry blocks hold DAT or inode entries. The allocator caches recently used descriptor, bitmap, and entry buffer heads in `mi_palloc_cache`, protected by a spinlock. Updates become persistent through dirty buffer marking and NILFS segment writing.

## Dependencies and Integration Points

This file depends on NILFS metadata-file helpers in `mdt.h`, allocator definitions in `alloc.h`, buffer heads, folio kmap helpers, little-endian bit operations, block-group locks, and NILFS warning/error reporting. It is used by DAT and ifile-style metadata layers and indirectly by bmap pointer allocation.

## Risks and Edge Cases

The allocator mixes buffer-head caching, folio local mappings, and per-group spinlocks; incorrect release or stale cache invalidation can leak buffers or corrupt allocation state. Freeing an already-free entry is detected only as a warning. `nilfs_palloc_prepare_alloc_entry()` must handle wrap/no-wrap semantics and descriptor growth limits correctly. `nilfs_palloc_freev()` assumes useful grouping of input entries but still guards group transitions. Block size greater than page size is explicitly unsupported by descriptor initialization.

## Test Signals

Exercise DAT/inode allocation until descriptor growth, no-wrap and wrap allocation, abort paths after prepared allocations/frees, batched free across groups and entry-block boundaries, freeing already-free entries, cache clear/destroy under unmount, ENOSPC behavior, metadata I/O errors, and fsck/recovery after crashes between prepare and commit at higher layers.
