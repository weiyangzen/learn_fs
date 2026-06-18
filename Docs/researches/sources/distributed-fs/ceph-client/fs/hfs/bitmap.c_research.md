# sources/distributed-fs/ceph-client/fs/hfs/bitmap.c

## Purpose
`bitmap.c` manages the HFS volume bitmap: finding and setting free allocation blocks, clearing allocated ranges, updating free block counts, and marking the bitmap dirty.

## Important APIs, Types, And Functions
`hfs_find_set_zero_bits` scans a big-endian 32-bit bitmap for the first zero bit at or after an offset, sets up to the requested number of consecutive zero bits, and returns the start. `hfs_vbm_search_free` is the public allocator search that locks the bitmap, tries the requested goal, wraps to zero if needed, decrements `free_ablocks`, and marks the bitmap dirty. `hfs_clear_vbm_bits` clears a range, increments `free_ablocks`, and marks the bitmap dirty.

## Control Flow
Allocation checks for nonzero requested count, locks `bitmap_lock`, scans the in-memory bitmap for a free run, wraps when the goal scan fails, reports full disk by returning zero length, updates free count, marks dirty, and unlocks. The low-level scanner handles partial first words, full 32-bit words, and partial tail words in left-to-right HFS bit order.

Freeing validates nonzero count and range, locks the bitmap, masks out partial first word, clears full words, masks the tail, updates the free count, unlocks, and marks the bitmap dirty.

## State And Persistence
State lives in `HFS_SB(sb)->bitmap`, `fs_ablocks`, and `free_ablocks`. Dirty marking schedules persistence through HFS metadata writeback; the file itself mutates the in-memory big-endian bitmap words.

## Dependencies And Integration Points
The code depends on HFS superblock state, `bitmap_lock`, endian conversion helpers, debug logging, and `hfs_bitmap_dirty`. Extent and allocation code call these functions to reserve or release allocation blocks.

## Risks And Test Signals
Risks include off-by-one wrap behavior, mismatched big-endian bit order, free count drift, clearing out-of-range ranges, and lack of already-clear detection despite comments mentioning that error. Signals include allocation/free stress tests, fsck free block count checks, fragmented bitmap tests, full-disk tests, and endian-sensitive image tests.
