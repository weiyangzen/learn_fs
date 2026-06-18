# sources/distributed-fs/ceph-client/fs/ntfs3/bitmap.c

## Purpose
Implements NTFS3 bitmap-window allocation support. It tracks free clusters/MFT records using per-window free counters and two red-black trees of free extents, while falling back to scanning the on-disk bitmap when the cache is incomplete.

## Important APIs, Types, And Functions
`wnd_init()` initializes a `wnd_bitmap`, allocates `free_bits`, and calls `wnd_rescan()`. `wnd_rescan()` reads bitmap windows through the runlist and builds extent trees. `wnd_find()` searches for allocatable free space by hint, biggest extent, or bitmap scan and can mark the result used. `wnd_set_free()`, `wnd_set_used()`, and `wnd_set_used_safe()` mutate persistent bitmap buffers and update caches. `wnd_is_free()` and `wnd_is_used()` query ranges. `wnd_extend()` grows a bitmap. `wnd_zone_set()` reserves an allocation zone. `ntfs_trim_fs()` issues discard for free ranges. `ntfs_bitmap_set_le()`, `ntfs_bitmap_clear_le()`, and `ntfs_bitmap_weight_le()` provide little-endian bitmap primitives.

## Control Flow
Initialization scans each bitmap block, computes free counts, coalesces free extents across window boundaries, and limits the tree to `NTFS_MAX_WND_EXTENTS`. Allocation first checks aggregate zeroes and largest extent, then tries hint-based lookup, largest cached extent, or a raw bitmap scan. Marking bits used/free maps the window through `wnd_map()`, locks the buffer, changes bits, marks it dirty, and updates extent trees.

## State And Persistence
Persistent state is the on-disk `$Bitmap` or `$MFT/$BITMAP` buffer data. Runtime state includes `free_bits[]`, `total_zeroes`, `extent_max`, `extent_min`, `start_tree`, `count_tree`, `zone_bit/end`, `uptodated`, and `run`. The cache may become approximate (`uptodated = -1`) when extent count or allocation failures prevent complete tracking.

## Dependencies And Integration Points
Used by NTFS3 allocation paths in `attrib.c` and filesystem trimming. Depends on runlists, buffer heads, block mapping, discard helpers, and bit predicates from `bitfunc.c`.

## Risks And Edge Cases
Cache and disk bitmap must remain synchronized. Tree capping can force fallback scans, making `extent_max` approximate. Zone exclusion must prevent allocations from reserved regions while allowing zones to be restored. `wnd_set_used_safe()` intentionally tolerates partially used ranges but must report how many bits it changed. Errors from `wnd_map()` or buffer reads can cause allocation failure or conservative no-space behavior.

## Test Signals
Test allocation with hints, full/partial allocation flags, zone reservation, tree cap behavior, rescan after cache invalidation, free/used transitions across window boundaries, bitmap extension, discard ranges with `minlen`, little-endian set/clear/weight helpers, and crash-consistency checks after marked-dirty buffers.
