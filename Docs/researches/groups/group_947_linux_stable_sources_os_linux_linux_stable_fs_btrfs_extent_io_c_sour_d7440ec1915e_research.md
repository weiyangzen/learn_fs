# Group Research: group_947_linux_stable_sources_os_linux_linux_stable_fs_btrfs_extent_io_c_sour_d7440ec1915e

Scope confirmed against `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/extent_io.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/extent_io.c

## Purpose

`extent_io.c` is Btrfs' main extent I/O implementation for page-cache data I/O and btree metadata extent-buffer I/O. It connects inode extent maps, delalloc state, ordered extents, folio/subpage state, bio construction, metadata buffer lifetime, and extent-buffer byte access helpers.

## Main Responsibilities

- Data read path:
  - `btrfs_read_folio()` and `btrfs_readahead()` lock stable file ranges with `lock_extents_for_read()`, call `btrfs_do_readpage()`, and submit accumulated bios.
  - `btrfs_do_readpage()` resolves extent maps, handles holes, inline extents, compressed extents, fsverity verification, EOF zeroing, and readahead expansion.
  - `end_bbio_data_read()` updates folio uptodate state, zeroes post-i_size ranges, verifies fsverity data, and unlocks folios or subpage ranges.

- Data writeback path:
  - `btrfs_writepages()` drives `extent_write_cache_pages()` with a `btrfs_bio_ctrl`.
  - `extent_writepage()` handles EOF invalidation/zeroing, delalloc conversion, COW fixup, sector submission, error propagation, and folio unlocking.
  - `writepage_delalloc()` finds and locks delalloc ranges, runs `btrfs_run_delalloc_range()`, handles async compression/inline paths, and maintains subpage submit bitmaps.
  - `extent_write_locked_range()` submits already-locked ranges, used when delalloc has already produced ordered extents.

- Bio assembly:
  - `struct btrfs_bio_ctrl` tracks the current bio, next file offset, compression type, ordered-extent boundary, checksum generation optimization, writeback control, submit bitmap, readahead context, and last compressed extent-map start.
  - `submit_extent_folio()` merges compatible folio ranges into bios, splits at ordered extent boundaries and bio limits, and tracks max read extent generation.
  - `submit_one_bio()` chooses normal vs compressed read submission and applies checksum commit-root lookup optimization for old data extents.

- Metadata extent-buffer I/O:
  - `btree_writepages()` scans `fs_info->buffer_tree` xarray marks, tags dirty buffers, handles zoned metadata write-pointer constraints, and writes dirty extent buffers.
  - `lock_extent_buffer_for_io()`, `write_one_eb()`, `prepare_eb_write()`, and `end_bbio_meta_write()` coordinate metadata dirty/writeback state, folio writeback state, cgroup accounting, and error reporting.
  - `read_extent_buffer_pages_nowait()` and `read_extent_buffer_pages()` submit metadata reads and validate parent checks in `end_bbio_meta_read()`.

- Extent-buffer allocation and lifetime:
  - Extent buffers are slab-allocated through `extent_buffer_cache`.
  - `alloc_extent_buffer()` creates or finds xarray-backed metadata buffers, attaches folios, handles subpage metadata state, sets lockdep class, and installs `EXTENT_BUFFER_TREE_REF`.
  - `find_extent_buffer()`, `free_extent_buffer()`, `free_extent_buffer_stale()`, `try_release_extent_buffer()`, and `try_release_subpage_extent_buffer()` manage concurrent lookup/release, stale buffers, tree references, RCU freeing, and folio private state.
  - Dummy and cloned buffers are provided by `alloc_dummy_extent_buffer()` and `btrfs_clone_extent_buffer()` for tests and safe leaf snapshots.

- Extent-buffer content access:
  - `read_extent_buffer()`, `write_extent_buffer()`, `memzero_extent_buffer()`, `copy_extent_buffer*()`, `memcmp_extent_buffer()`, `memcpy_extent_buffer()`, and `memmove_extent_buffer()` abstract byte operations across one or multiple folios.
  - Bitmap helpers operate byte-wise to preserve little-endian on-disk bitmap layout and tolerate page-straddling bitmap items.

## Important Concurrency and Correctness Points

- Read paths lock inode extent-state ranges to stabilize extent maps against ordered extent completion. `can_skip_ordered_extent()` avoids deadlock by skipping ordered extents whose folios are locked and already dirty/uptodate.
- Delalloc writeback is tightly coupled to folio locks, extent-state bits, ordered extents, and subpage bitmaps; error paths explicitly finish ordered I/O when no bio will do it.
- Metadata buffers use xarray marks as dirty/writeback tags instead of normal page-cache traversal. Extent-buffer references include a special xarray tree reference tracked by `EXTENT_BUFFER_TREE_REF`.
- Subpage support is pervasive. Folio private data can represent either data or metadata subpage state, and release paths must not detach private state while other extent buffers in the same folio still exist.
- Zoned filesystems add ordering constraints: metadata writeback is serialized with zoned metadata locks, and clearing dirty buffers may mark `EXTENT_BUFFER_ZONED_ZEROOUT` instead of dropping dirty state.

## Dependencies and Callers

This file depends heavily on `extent-io-tree`, `extent_map`, ordered extents, compression, bio submission, file items, fsverity, subpage helpers, transaction state, and zoned block-group logic. Its exported functions are used by Btrfs address-space operations, btree block reads, transaction commit/writeback, fsync/logging paths, and folio release/invalidation hooks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/extent_io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/extent_io.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/extent_io.h

## Purpose

`extent_io.h` declares the public interface and core data structures for Btrfs extent I/O and metadata extent buffers. It is the contract used by Btrfs data I/O, btree I/O, folio release, metadata accessors, and delalloc helpers.

## Key Definitions

- `EXTENT_BUFFER_*` bit indexes:
  - Track extent-buffer uptodate, dirty, tree-ref, stale, writeback, unmapped, write error, zoned zeroout, and reading states.

- Page operation flags:
  - `PAGE_UNLOCK`, `PAGE_START_WRITEBACK`, `PAGE_END_WRITEBACK`, and `PAGE_SET_ORDERED` describe batched folio operations used by delalloc cleanup and writeback transitions.

- `EXTENT_FOLIO_PRIVATE`:
  - Sentinel for non-subpage data folios controlled by Btrfs extent I/O.

- Bitmap macros:
  - `BIT_BYTE`, `BITMAP_FIRST_BYTE_MASK`, and `BITMAP_LAST_BYTE_MASK` support byte-granular extent-buffer bitmap operations.

- `struct extent_buffer`:
  - Represents a Btrfs metadata block in memory.
  - Stores logical `start`, `len`, folio size/shift, state flags, fs pointer, optional contiguous `addr`, reference state, read mirror, writeback inhibitor count, log-tree index, RCU head, tree lock, and an inline folio pointer array.
  - `addr` is an optimization for physically contiguous storage that avoids cross-folio handling.

- `struct btrfs_eb_write_context`:
  - Tracks a metadata writeback control, target extent buffer, and optional zoned block group.

- `struct extent_changeset`:
  - Tracks changed byte counts and optionally changed ranges through a `ulist`.
  - Supports a bytes-only mode via `EXTENT_CHANGESET_BYTES_ONLY` to avoid atomic allocations when callers do not need range iteration.

## Inline Helpers

- `offset_in_eb_folio()` computes offsets for the extent buffer's folio size.
- `get_eb_offset_in_folio()` handles both page-sized metadata blocks and subpage nodesize cases where multiple extent buffers share one folio.
- `get_eb_folio_index()` maps an extent-buffer-relative offset to a folio slot.
- `num_extent_pages()` and `num_extent_folios()` distinguish logical page count from runtime folio count, allowing future higher-order folio support.
- `extent_buffer_uptodate()` checks the buffer-level uptodate flag.
- `wait_on_extent_buffer_writeback()` waits on the extent-buffer writeback bit.

## Exported Interface Categories

- Data I/O:
  - `btrfs_read_folio()`, `btrfs_readahead()`, `btrfs_writepages()`, `extent_write_locked_range()`.

- Metadata I/O:
  - `btree_writepages()`, `btrfs_btree_wait_writeback_range()`, `read_extent_buffer_pages*()`.

- Extent-buffer lifecycle:
  - `alloc_extent_buffer()`, `alloc_dummy_extent_buffer()`, `btrfs_clone_extent_buffer()`, `find_extent_buffer()`, `free_extent_buffer()`, `free_extent_buffer_stale()`.

- Extent-buffer memory access:
  - Read/write/copy/move/zero/compare helpers plus bitmap get/set/clear helpers.

- Folio and delalloc state:
  - `set_folio_extent_mapped()`, `clear_folio_extent_mapped()`, `try_release_extent_mapping()`, `try_release_extent_buffer()`, `extent_clear_unlock_delalloc()`, `extent_invalidate_folio()`.

- Allocation helpers:
  - `btrfs_alloc_page_array()` and `btrfs_alloc_folio_array()`.

- Debug/test hooks:
  - Leak checking and `find_lock_delalloc_range()` under sanity tests.

## Design Notes

The header encodes the split between data folio state and metadata extent-buffer state while hiding subpage and multi-folio details from most callers. Its helpers are carefully documented because extent-buffer offsets differ between normal nodesize >= PAGE_SIZE layouts and subpage metadata layouts.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/extent_io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/extent_map.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/extent_map.c

## Purpose

`extent_map.c` implements Btrfs' in-memory extent map cache for file extents. Extent maps describe logical file ranges and their backing disk ranges, holes, inline extents, compression state, preallocation, pinning, logging state, and fsync generations.

## Core Data Structure Behavior

- Extent maps live in an inode-local red-black tree (`extent_map_tree.root`) protected by an rwlock.
- Modified extents are tracked on `extent_map_tree.modified_extents` for fast fsync.
- Each map is refcounted. Tree insertion takes a reference; lookups take a reference; removals and callers drop references separately.
- `btrfs_extent_map_init()` and `btrfs_extent_map_exit()` manage the slab cache.

## Lookup and Insertion

- `tree_insert()` rejects overlapping ranges and validates neighbor overlap.
- `tree_search()` finds either an intersecting extent or a neighboring extent.
- `btrfs_lookup_extent_mapping()` returns the first intersecting map.
- `btrfs_search_extent_mapping()` may return a nearby map even if it does not strictly intersect, used when resolving insertion races.
- `btrfs_add_extent_mapping()` inserts a new map or handles `-EEXIST` by returning the existing map or fitting the new map between neighbors through `merge_extent_mapping()`.

## Merging

- `can_merge_extent_map()` rejects pinned, compressed, logging, or modified-list maps.
- `mergeable_maps()` requires logical adjacency, compatible flags, and either physical adjacency or matching hole/inline sentinels.
- `merge_ondisk_extents()` updates physical extent fields when adjacent regular extents are merged.
- `try_merge_map()` merges with previous and next neighbors when safe and when the map is not held by other users.

## Removal and Replacement

- `btrfs_remove_extent_mapping()` removes a map from the rb-tree and modified list when appropriate.
- `replace_extent_mapping()` swaps an existing tree node with a new map while preserving modified-list semantics.
- `btrfs_drop_extent_map_range()` drops all maps intersecting a range, splitting boundary maps when memory is available.
  - If splitting fails for a modified map, it removes the whole map and marks the inode for full fsync so fast fsync will not miss new extents.
  - The fast path `drop_all_extent_maps_fast()` removes the entire tree when dropping `[0, U64_MAX]` without skipping pinned maps.
- `btrfs_replace_extent_map_range()` repeatedly drops overlapping maps and inserts a replacement until `-EEXIST` no longer occurs.

## Ordered Extent and Fsync Integration

- `btrfs_unpin_extent_cache()` clears `EXTENT_FLAG_PINNED` after writeback completion and records the generation that inserted the file item.
- `btrfs_split_extent_map()` splits a pinned modified extent map when an ordered extent is split, replacing the original with pre/mid maps and preserving modified tracking.
- `btrfs_clear_em_logging()` clears logging state and tries to merge the map.

## Shrinker

- `btrfs_free_extent_maps()` schedules asynchronous reclaim through `em_shrinker_work`.
- `btrfs_extent_map_shrinker_worker()` scans filesystem roots and inodes, removing reclaimable extent maps under memory pressure.
- `btrfs_scan_inode()` skips pinned maps, sets full-sync when removing recent modified maps, and stops on scheduling/lock contention or filesystem closing.
- `find_first_inode_to_shrink()` avoids blocking on busy extent-map locks and skips inodes with empty trees.

## Correctness Notes

- Extent maps can be merged and therefore do not always correspond one-to-one to on-disk file extent items.
- Compressed extents are deliberately not merged because their physical size matters.
- Removal of modified extents is tied to fsync correctness. If an extent needed for fast fsync could be lost, the inode is forced to full sync.
- The code validates alignment and physical fields in debug builds via `validate_extent_map()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/extent_map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/extent_map.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/extent_map.h

## Purpose

`extent_map.h` defines the in-memory file extent map representation and declares the extent-map tree API used by Btrfs read, writeback, fiemap, fsync, and reclaim paths.

## Key Constants

- `EXTENT_MAP_LAST_BYTE` separates real disk bytenrs from sentinel values.
- `EXTENT_MAP_HOLE` marks logical holes.
- `EXTENT_MAP_INLINE` marks inline file extents.

## Extent Map Flags

- `EXTENT_FLAG_PINNED`: entry is not yet persisted and must not be evicted.
- `EXTENT_FLAG_COMPRESS_ZLIB`, `EXTENT_FLAG_COMPRESS_LZO`, `EXTENT_FLAG_COMPRESS_ZSTD`: compression type bits.
- `EXTENT_FLAG_PREALLOC`: preallocated extent.
- `EXTENT_FLAG_LOGGING`: extent is being logged.
- `EXTENT_FLAG_MERGED`: runtime-only indicator that adjacent maps were merged.

## `struct extent_map`

The structure is intentionally compact because many instances can exist. It stores:

- `rb_node` for the inode's extent rb-tree.
- Logical range: `start`, `len`.
- Physical/on-disk fields: `disk_bytenr`, `disk_num_bytes`, `offset`, `ram_bytes`.
- `generation` used for fsync and merged-map generation tracking.
- `flags`, `refs`, and `list` for modified extent tracking.

The comments explicitly distinguish regular, compressed, hole, and inline extent semantics.

## `struct extent_map_tree`

Contains the rb-tree root, modified extent list, and rwlock. Each Btrfs inode has one to cache file extent mappings.

## Inline Helpers

- `btrfs_extent_map_set_compression()` sets compression flag bits.
- `btrfs_extent_map_compression()` decodes compression type.
- `btrfs_extent_map_is_compressed()` checks compression efficiently.
- `btrfs_extent_map_in_tree()` checks rb-tree membership.
- `btrfs_extent_map_block_start()` returns physical start:
  - compressed extents use `disk_bytenr`;
  - regular extents use `disk_bytenr + offset`;
  - holes/inline return the sentinel.
- `btrfs_extent_map_end()` returns exclusive logical end and handles overflow.

## Exported API

The header exposes initialization, allocation/free, lookup/search, insertion, removal, range drop/replace, split, unpin, logging clear, and shrinker scheduling/init functions.

## Design Notes

The header documents that extent maps are cache objects, not exact persistent file extent records after merging. This distinction is essential for read I/O, fiemap, and fsync correctness.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/extent_map.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/fiemap.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/fiemap.c

## Purpose

`fiemap.c` implements Btrfs' `FIEMAP` ioctl support. It reports logical-to-physical file extent mappings while handling Btrfs-specific realities: holes, prealloc extents, inline data, compression, delalloc, shared extents, ordered extent completion, and concurrent tree changes.

## Fiemap Cache

`struct fiemap_cache` buffers and merges fiemap entries before copying them to the user-provided fiemap buffer.

It serves two purposes:

- Merge contiguous logical and physical extents with identical flags.
- Avoid deadlocks when the fiemap output buffer is mmaped to the same file, by buffering entries while the file range and tree path are locked, then flushing after unlocking.

`emit_fiemap_extent()` is the central merge/cache function. It handles overlapping or stale ranges caused by ordered extents completing while the path/range had to be unlocked. When the intermediate cache is full, it returns `BTRFS_FIEMAP_FLUSH_CACHE`, causing the main scan to unlock, flush, and restart from `next_search_offset`.

## Tree Scanning

- `fiemap_search_slot()` finds the first file extent item at or before the requested offset.
- It clones the current leaf with `btrfs_clone_extent_buffer()` before long processing so fiemap does not hold a real btree leaf locked during expensive shared-extent checks.
- `fiemap_next_leaf_item()` advances within the cloned leaf or moves to the next leaf, recloning as needed.
- `fiemap_find_last_extent_offset()` finds the last non-hole file extent end so the final emitted extent can be tagged `FIEMAP_EXTENT_LAST` when appropriate.

## Hole, Prealloc, and Delalloc Handling

`fiemap_process_hole()` processes implicit holes, explicit hole file extent items, and prealloc extents.

- For holes, it searches the inode io tree for delalloc ranges and emits them as `FIEMAP_EXTENT_DELALLOC | FIEMAP_EXTENT_UNKNOWN`.
- For prealloc extents, it emits unwritten physical ranges with `FIEMAP_EXTENT_UNWRITTEN`, splitting around delalloc ranges.
- Shared state for prealloc extents is checked through `btrfs_is_data_extent_shared()` only when output extents are requested.
- Searches are capped at `i_size` for delalloc because no delalloc exists beyond EOF.

## Main Algorithm

`extent_fiemap()`:

1. Allocates the intermediate cache, backref share-check context, and btree path.
2. Rounds the requested range to sectorsize boundaries.
3. Locks the corresponding inode io-tree range to stabilize delalloc and ordered extent state.
4. Finds the last extent and the first relevant file extent item.
5. Walks file extent items, handling:
   - implicit holes before the next file extent item,
   - inline extents with `FIEMAP_EXTENT_DATA_INLINE | FIEMAP_EXTENT_NOT_ALIGNED`,
   - prealloc extents through `fiemap_process_hole()`,
   - explicit holes through `fiemap_process_hole()`,
   - regular extents with optional `FIEMAP_EXTENT_ENCODED` for compression and `FIEMAP_EXTENT_SHARED` for shared extents.
6. Checks trailing EOF delalloc or holes.
7. Tags the final cached extent as `FIEMAP_EXTENT_LAST` when no later real or delalloc extent exists.
8. Unlocks, flushes cached entries, emits the final cached entry, and frees resources.

## Public Entry Point

`btrfs_fiemap()` prepares the request with `fiemap_prep()`, optionally waits for ordered extents for `FIEMAP_FLAG_SYNC`, takes the Btrfs inode shared lock, repeats ordered waiting to close the race with new writes, calls `extent_fiemap()`, and unlocks.

## Correctness Notes

- The implementation primarily reports file extent items, consulting the io tree only for holes/prealloc ranges where delalloc may exist.
- Compression requires extra sync handling because initial writeback can only start async compression; a second ordered wait is needed for stable reporting under `FIEMAP_FLAG_SYNC`.
- Leaf cloning avoids long-held btree locks and lockdep issues during backref walking.
- Cache flush/restart logic prevents missing newly inserted extents after unlocking and avoids overlapping reports when ordered extents complete concurrently.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/fiemap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/fiemap.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/fiemap.h

## Purpose

`fiemap.h` is the small public header for Btrfs fiemap support.

## Contents

- Header guard: `BTRFS_FIEMAP_H`.
- Includes `<linux/fiemap.h>` for `struct fiemap_extent_info`.
- Declares:

```c
int btrfs_fiemap(struct inode *inode, struct fiemap_extent_info *fieinfo,
                 u64 start, u64 len);
```

## Role

This header exposes the fiemap entry point implemented in `fiemap.c` to the rest of the Btrfs inode/file operation code. It has no private structs or inline helpers; all implementation detail stays in `fiemap.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/fiemap.h -->