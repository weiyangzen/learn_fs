# sources/distributed-fs/ceph-client/fs/squashfs/cache.c

## Purpose

`cache.c` implements the generic cache used for SquashFS metadata, fragments, and the optional file-data intermediate buffer. It avoids repeated reads and decompressions of packed metadata/fragment blocks and provides metadata stream reading across compressed metadata-block boundaries.

## Important APIs, Types, and Functions

Public functions are `squashfs_cache_init()`, `squashfs_cache_delete()`, `squashfs_cache_get()`, `squashfs_cache_put()`, `squashfs_copy_data()`, `squashfs_read_metadata()`, `squashfs_get_fragment()`, `squashfs_get_datablock()`, and `squashfs_read_table()`. Key types are `struct squashfs_cache`, `struct squashfs_cache_entry`, and `struct squashfs_page_actor`.

## Control Flow

`squashfs_cache_get()` looks for a block in a round-robin cache. On miss, it waits if all entries are referenced, otherwise claims an unused entry, marks it pending, fills it with `squashfs_read_data()`, clears pending, and wakes waiters. On hit, it increments the refcount and waits if another task is still filling the entry. `squashfs_read_metadata()` repeatedly gets metadata blocks, copies from the current offset, advances to `entry->next_index`, and releases entries.

## State and Persistence Behavior

The cache persists per mounted filesystem in `squashfs_sb_info`. Each entry tracks block id, decompressed length, refcount, pending/error state, wait queues, backing page-sized buffers, and actor. The cache is read-only after fill except for eviction/reuse metadata.

## Dependencies and Integration Points

It depends on `squashfs_read_data()` for fills and `page_actor` for decompression destinations. Metadata readers across the filesystem use `squashfs_read_metadata()`. `super.c` allocates metadata, fragment, and read-page caches and releases them on mount failure/unmount.

## Risks and Edge Cases

Concurrency correctness depends on refcount, `unused`, pending state, and wait queue updates under the spinlock. Malformed metadata offsets or negative lengths return `-EIO`. `squashfs_copy_data()` supports `buffer == NULL` for skip/count behavior, which callers rely on heavily; incorrect use can desynchronize metadata offsets.

## Test Signals

Parallel directory/stat/read workloads should cover cache waiters and refcounts. Corrupt metadata-block length, bad offsets, allocation-failure injection, fragment-heavy small files, and xattr/symlink metadata spanning blocks are useful targeted tests.
