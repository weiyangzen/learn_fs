# sources/distributed-fs/ceph-client/fs/btrfs/tests/free-space-tests.c

## Purpose

`free-space-tests.c` validates the in-memory free-space cache for block groups. It tests extent-only entries, bitmap-only entries, mixed extent/bitmap removal, stealing contiguous free space from bitmap entries into extent entries, and the free-space bytes index.

## Important APIs, Types, And Functions

- `test_extents()` checks full, front, tail, and middle removal from extent entries.
- `test_bitmaps()` checks full and middle removal from bitmap entries and removal across two bitmap regions.
- `test_bitmaps_and_extents()` checks overlapping removals when free space is represented by both extents and bitmaps.
- `test_use_bitmap()` and `test_steal_space_from_bitmap_to_extent()` force bitmap selection to build targeted layouts, then validate coalescing/stealing behavior around adjacent extent/bitmap free ranges.
- `check_num_extents_and_bitmaps()` and `check_cache_empty()` assert free-space-control counters and allocation behavior.
- `bytes_index_use_bitmap()` and `test_bytes_index()` validate ordering and recalculation of `free_space_bytes` for extents and bitmaps.
- `btrfs_test_free_space_cache()` builds dummy fs/block group/root state and runs all groups.

## Control Flow

The entry point creates a dummy fs_info, a block group large enough to cross bitmap boundaries, and a dummy extent-tree root, then inserts the root globally. It runs simple extent tests, bitmap tests, mixed tests, bitmap-to-extent stealing tests, and bytes-index tests. Each subtest adds free-space entries, removes or allocates ranges with production cache helpers, and checks existence/counters.

The stealing test temporarily replaces `cache->free_space_ctl->op` with a test policy that forces bitmap use after at least one extent exists. It constructs adjacent extent/bitmap ranges on both sides, leaves small non-contiguous bitmap ranges behind, then verifies that large contiguous ranges can be allocated as one extent and that only the small bitmap ranges remain.

The bytes-index test validates descending order by bytes, bitmap entry ordering, max-extent-size recalculation after failed searches, and reordering after later additions.

## State And Persistence Behavior

State is entirely in `cache->free_space_ctl`: rb-trees, bitmap entries, extent entries, free-space counters, bitmap counts, and bytes-index ordering. The dummy root is registered because production free-space helpers expect global root context, but no persistent free-space tree is written here.

## Dependencies And Integration Points

This file depends on free-space-cache internals, block group scaffolding, dummy root/fs helpers, extent-tree root registration, and allocation helpers such as `btrfs_find_space_for_alloc()`, `btrfs_add_free_space()`, `btrfs_remove_free_space()`, `test_add_free_space_entry()`, and `test_check_exists()`.

## Risks

The test temporarily overrides free-space operations; failing before restoration would leave test-local state corrupted, though the final test restores before returning on the normal path. The scenarios are deterministic but do not model concurrent allocation/free. Some expectations depend on current bitmap threshold and bytes-index semantics.

## Test Signals

Failures report leftover free ranges, missing ranges, unexpected counters, wrong allocation offsets, wrong max extent sizes, or bytes-index misordering. A zero return from `btrfs_test_free_space_cache()` means the in-memory free-space cache scenarios passed for the requested sectorsize/nodesize.
