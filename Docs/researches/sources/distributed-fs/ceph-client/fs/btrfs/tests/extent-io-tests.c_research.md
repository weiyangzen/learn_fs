# sources/distributed-fs/ceph-client/fs/btrfs/tests/extent-io-tests.c

## Purpose

`extent-io-tests.c` tests several Btrfs extent I/O primitives: delalloc range discovery and page locking, extent-buffer bitmap operations, clear-range search in an extent-state tree, and extent-buffer memory copy/move behavior across pages.

## Important APIs, Types, And Functions

- `process_page_range()` walks contiguous folios in an inode mapping, optionally checks locking, unlocks, and releases them.
- `extent_flag_to_str()` and `dump_extent_io_tree()` provide failure diagnostics for extent-state trees.
- `test_find_delalloc()` exercises `find_lock_delalloc_range()` against dirty page cache and `EXTENT_DELALLOC` ranges.
- `check_eb_bitmap()`, `test_bitmap_set()`, `test_bitmap_clear()`, `__test_eb_bitmaps()`, and `test_eb_bitmaps()` compare extent-buffer bitmap helpers against a normal bitmap.
- `test_find_first_clear_extent_bit()` checks `btrfs_find_first_clear_extent_bit()` on empty trees, holes between set ranges, partial flag matches, and beyond-end searches.
- `dump_eb_and_memory_contents()`, `verify_eb_and_memory()`, `init_eb_and_memory()`, and `test_eb_mem_ops()` compare extent-buffer memory operations with normal `memcpy()`/`memmove()`.
- `btrfs_test_extent_io()` runs all groups.

## Control Flow

`test_find_delalloc()` allocates a dummy inode/root/fs_info, creates and dirties enough pages for two max-size extents, pins the first locked page, sets delalloc ranges, and checks that `find_lock_delalloc_range()` returns expected start/end and locks all pages in the returned range. It also checks behavior when no matching range exists and when a page inside the delalloc span is no longer dirty.

Bitmap tests allocate an extent buffer at offset 0 and again at a sectorsize offset, then run full clear/set, same-byte, cross-byte, cross-page, and pseudo-random bit patterns. Clear-range tests mutate an `extent_io_tree` with `CHUNK_TRIMMED`/`CHUNK_ALLOCATED` flags and validate returned holes. Memory operation tests initialize an extent buffer and mirror memory with random bytes, then compare normal memory operations to `memcpy_extent_buffer()` and `memmove_extent_buffer()`.

## State And Persistence Behavior

State is in page cache folios, Btrfs inode `io_tree`, dummy extent buffers, and local bitmaps/memory buffers. No disk persistence occurs. Cleanup unlocks/releases pages, clears extent bits, frees extent buffers, and frees dummy roots/fs_info.

## Dependencies And Integration Points

The file integrates with Linux page cache/folio APIs, Btrfs extent I/O trees, extent buffer accessors, dummy inode/root setup, and memory helpers. It protects behavior used by writeback/delalloc, metadata bitmap manipulation, and metadata buffer copies.

## Risks

`test_find_delalloc()` is sensitive to page size, dirty page state, and lock cleanup; a missed unlock or put can destabilize later tests. It validates representative page/extent layouts but not true concurrent writeback races. Bitmap and memory tests provide broad boundary coverage but are limited to dummy buffers.

## Test Signals

Failures report missing delalloc ranges, wrong start/end, unlocked pages, bitmap mismatches with byte dumps, wrong clear-range results, or extent-buffer/memory divergence. `dump_extent_io_tree()` is used on extent-tree failures.
