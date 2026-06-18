# sources/distributed-fs/ceph-client/fs/nilfs2/alloc.h

## Purpose

`alloc.h` declares the persistent allocator interface used by NILFS2 metadata files. It defines the request object, cache object, geometry helper, bit-operation aliases, and prepare/commit/abort API implemented in `alloc.c`.

## Important APIs, Types, and Functions

`nilfs_palloc_entries_per_group()` derives group capacity from block size in bits. `struct nilfs_palloc_req` carries the target or returned entry number plus descriptor, bitmap, and entry buffer heads. `struct nilfs_bh_assoc` pairs a block offset with a cached buffer head. `struct nilfs_palloc_cache` stores the previous descriptor, bitmap, and entry buffers under a spinlock.

Public functions initialize allocator block groups, retrieve entry blocks, compute entry offsets, count maximum entries, prepare/commit/abort allocations, prepare/commit/abort frees, batch free entries, and manage caches. Bit aliases bind NILFS allocator operations to ext2 atomic little-endian bitops and generic little-endian find-bit helpers.

## Control Flow

Callers use a two-phase pattern. For allocation, set an initial `pr_entry_nr`, call prepare, initialize or link the returned object, then commit or abort. For free, set `pr_entry_nr`, prepare, then commit or abort. Entry data access uses `nilfs_palloc_get_entry_block()` and `nilfs_palloc_entry_offset()` after an entry number is known.

## State and Persistence Behavior

The header models persistent allocator updates but does not write state itself. The request retains buffer-head references across prepare/commit/abort boundaries. The cache retains buffer references between allocator calls and must be cleared/destroyed during metadata inode teardown.

## Dependencies and Integration Points

It depends on Linux buffer heads, filesystem types, and NILFS on-disk allocator descriptors. It is included by DAT, ifile, bmap, and other metadata code that needs persistent entry numbering.

## Risks and Edge Cases

Callers must always complete a prepared request with commit or abort to release buffers and preserve bitmap/descriptor consistency. The bit operation aliases assume little-endian on-disk bitmaps. Cache users must hold/release references correctly and clear caches when metadata blocks are deleted.

## Test Signals

Compile-time tests should catch signature drift with DAT/ifile/bmap callers. Runtime tests should inspect allocation/free rollback, cache teardown, bitmap endian correctness, and entry offset calculations across block sizes.
