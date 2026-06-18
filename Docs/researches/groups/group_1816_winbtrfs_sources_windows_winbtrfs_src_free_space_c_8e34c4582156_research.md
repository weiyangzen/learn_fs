# Group Research: group_1816_winbtrfs_sources_windows_winbtrfs_src_free_space_c_8e34c4582156

Scope confirmed against `Docs/research_subset_a.md`. The listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/free-space.c -->
# File Research: sources/windows/winbtrfs/src/free-space.c

## Purpose

`free-space.c` implements WinBtrfs per-chunk free-space tracking, legacy inode-backed free-space cache handling, Btrfs free-space-tree handling, and the rollback-aware in-memory list operations used by allocation, balance, and transaction commit paths. It can clear stale on-disk caches, load existing free-space state, reconstruct it from the extent tree, serialize it back to cache inodes or the free-space tree, and keep address-sorted and size-sorted free-space lists consistent as extents are allocated or freed.

## Core State

- `chunk::space`: Address-sorted list of free ranges available in a chunk.
- `chunk::space_size`: Size-sorted companion list for the same `space` nodes, ordered with larger entries first.
- `chunk::deleting`: Ranges becoming free in the current transaction; merged into serialized cache state when updating caches.
- `chunk::cache`: FCB for the legacy free-space cache inode associated with a chunk.
- `chunk::old_cache`: Holds an invalidated cache inode after deletion so later cleanup can finish safely.
- `chunk::cache_loaded`: Prevents repeated reconstruction/loading.
- `chunk::changed` and `chunk::space_changed`: Mark chunk metadata and free-space state as needing writeback.
- `CACHE_INCREMENTS`: Legacy cache inode allocation granularity in sectors, set to `64`.
- `superblock_stripe`: Temporary list node used to count chunk stripes occupied by Btrfs superblock mirrors so those protected regions are excluded from available free space.

## Cache Clearing

- `remove_free_space_inode()` opens a root-tree cache inode by object id, marks it dirty, excises all extents when it has data, marks it deleted, flushes the FCB, and releases it.
- `clear_free_space_cache()` deletes all root-tree `FREE_SPACE_CACHE_ID` items and removes the cache inodes they reference.
- It drops any matching `chunk::cache` FCBs already attached to chunks.
- If a free-space tree exists, it deletes all items from `Vcb->space_root`.
- If the filesystem uses the free-space-tree compat-ro feature, it reloads each unloaded chunk cache, then marks the chunk as changed so the free-space tree can be regenerated.

## In-Memory Free-Space List Helpers

- `add_space_entry()` allocates a `space` record and inserts it into an address-sorted list. It optionally inserts the same node into `list_size`, sorted by descending range size.
- `order_space_entry()` repositions one existing `space` node into the size-sorted list.
- `space_list_add2()` adds a free range to an arbitrary `space` list. It handles containment, overlap at either edge, adjacency, disjoint insertion, size-list updates, and optional rollback recording.
- `space_list_add()` marks the chunk changed and adds the range to `chunk::deleting`, not directly to `chunk::space`.
- `space_list_subtract2()` removes an allocated range from an arbitrary free-space list. It handles full deletion, start/end trimming, splitting one range into two ranges, size-list updates, and optional rollback recording.
- `space_list_subtract()` marks the chunk changed and subtracts from both committed free space and pending-deleting ranges.
- `space_list_merge()` adds every range from a source list into a destination list.
- `copy_space_list()` duplicates address-sorted `space` records into a new list for cache serialization.
- `add_rollback_space()` wraps a range change in a `rollback_space` record and appends either `ROLLBACK_ADD_SPACE` or `ROLLBACK_SUBTRACT_SPACE`.

## Legacy Cache Loading

- `load_stored_free_space_cache()` finds the root-tree `FREE_SPACE_CACHE_ID` item for the chunk and opens the inode it points to.
- In `load_only` mode, it only attaches the FCB and returns.
- It rejects zero-length cache files, chunks below 100 MiB, generation mismatches, malformed sizes, invalid checksums, unknown entry types, and total-space mismatches.
- It reads the whole cache inode, verifies the embedded cache generation, verifies per-sector CRC32C checksums, parses `FREE_SPACE_ENTRY` records, and decodes bitmap records with `load_free_space_bitmap()`.
- It calls `get_superblock_size()` and checks that parsed free space plus protected superblock space equals `chunk_size - used`.
- On invalid cache contents, it deletes the root-tree cache item, excises cache inode extents, marks the cache FCB deleted, moves it to `old_cache`, clears parsed free-space entries, and returns `STATUS_NOT_FOUND`.
- `load_free_space_bitmap()` inverts the on-disk bitmap dwords, initializes an `RTL_BITMAP`, finds clear runs, and adds those runs as free ranges.
- `get_superblock_size()` computes logical chunk space protected for Btrfs superblock mirror locations across RAID0/RAID10, RAID5, RAID6, and single/dup/RAID1/RAID1C3/RAID1C4 mappings.

## Free-Space Tree Loading

- `load_stored_free_space_tree()` requires `Vcb->space_root` and a valid `TYPE_FREE_SPACE_INFO` item for the chunk.
- It walks following free-space-tree items until leaving the chunk range.
- It adds `TYPE_FREE_SPACE_EXTENT` items directly as free ranges.
- It decodes `TYPE_FREE_SPACE_BITMAP` items by copying bitmap data to an aligned buffer, finding clear runs, and adding the corresponding free ranges.
- It merges adjacent parsed ranges after the walk.
- It validates item sizes but does not compare parsed free space to `chunk_size - used`.

## Cache Generation Fallback

- `load_free_space_cache()` chooses between free-space-tree loading, legacy cache loading, or reconstruction from the extent tree.
- If free-space-tree flags are present and valid, it loads from `Vcb->space_root`.
- Else if the superblock cache generation matches `generation - 1`, it tries the legacy inode-backed cache.
- If stored loading returns `STATUS_NOT_FOUND`, it reconstructs the free-space list by scanning the extent tree from the chunk start.
- It treats `TYPE_EXTENT_ITEM` ranges as used by their key offset and `TYPE_METADATA_ITEM` ranges as used by `node_size`.
- `load_cache_chunk()` skips already loaded chunks, calls `load_free_space_cache()`, protects superblock regions with `protect_superblocks(c)`, and marks the chunk cache loaded.

## Legacy Cache Allocation And Update

- `insert_cache_extent()` allocates physical storage for a cache inode using the filesystem data profile, preferring existing writable non-relocation chunks before allocating a new data chunk.
- `allocate_cache_chunk()` ensures one chunk has a legacy cache inode and enough allocated cache-file space.
- It counts current free-space entries plus pending-deleting entries, computes cache inode size with checksum area, generation field, entry padding, and `CACHE_INCREMENTS` alignment.
- It creates a new cache FCB and root-tree `FREE_SPACE_CACHE_ID` item when absent.
- It reallocates extents when the cache needs to grow or when existing cache extents sit in readonly or relocation chunks.
- `allocate_cache()` walks changed chunks of at least 100 MiB, allocates cache storage, and commits batched FCB/tree changes.
- `update_chunk_cache()` serializes one chunk's legacy cache inode by copying `space`, copying `deleting`, merging them, writing `FREE_SPACE_EXTENT` entries, updating inode metadata, updating the `FREE_SPACE_ITEM`, writing cache generation, calculating CRC32C checksums, and writing the cache file data.
- `update_chunk_caches()` writes legacy caches for changed chunks and then flushes pending partial RAID5/RAID6 stripes for changed parity chunks.

## Free-Space Tree Updating

- `update_chunk_cache_tree()` copies and merges `space` plus `deleting`, then reconciles `Vcb->space_root` with the merged list.
- It inserts missing `TYPE_FREE_SPACE_EXTENT` items, leaves matching extent items unchanged, deletes stale extent items, and deletes all bitmap items for the chunk.
- It updates an existing `TYPE_FREE_SPACE_INFO` item in place when possible, or deletes/reinserts it otherwise.
- It sets `FREE_SPACE_INFO.count` to the number of extent records and clears flags.
- It does not emit bitmap items; all output entries are extent items.
- `update_chunk_caches_tree()` sets `BTRFS_COMPAT_RO_FLAGS_FREE_SPACE_CACHE_VALID` and updates the free-space tree for changed chunks.

## Important Dependencies

- Tree operations: `find_item`, `find_next_item`, `insert_tree_item`, `delete_tree_item`, `keycmp`
- FCB and inode operations: `open_fcb`, `create_fcb`, `flush_fcb`, `free_fcb`, `reap_fcb`, `mark_fcb_dirty`, `add_fcb_to_subvol`
- Extent operations: `excise_extents`, `insert_extent_chunk`, `get_chunk_from_address`, `protect_superblocks`
- Allocation and chunk state: `alloc_chunk`, `chunk_lock`, `acquire_chunk_lock`, `release_chunk_lock`
- Rollback and batching: `add_rollback`, `clear_rollback`, `do_rollback`, `commit_batch_list`, `clear_batch_list`
- Checksums and time: `calc_crc32c`, `KeQuerySystemTime`, `win_time_to_unix`
- Windows kernel utilities: `ExAllocatePoolWithTag`, `ExFreePool`, `RTL_BITMAP`, `RtlFindFirstRunClear`, `RtlFindNextForwardRunClear`, `ERESOURCE`

## Notable Edge Cases

- Several comments question behavior when the sector size is not 4096 bytes.
- Legacy cache bitmap writing is not implemented, and free-space-tree updating deletes bitmap items and rewrites only extent items.
- `load_stored_free_space_cache()` has a FIXME before bitmap decoding to ensure bitmap reads cannot overflow the cache buffer.
- Legacy cache checksum calculation has FIXME comments for sectors fully inside the checksum area.
- `add_space_entry()` does not merge adjacent ranges; bulk loaders must merge afterward.
- `space_list_add2()` records rollback for most expansion/insertion cases, but the final contiguous-with-last-entry case grows the last entry without adding rollback state.
- `clear_free_space_cache()` initializes and clears rollback around legacy cache inode deletion, but later free-space-tree deletions are not wrapped in the same rollback path.
- `update_chunk_cache()` ignores cache data write errors by design, so callers may see success even when the legacy cache file was not refreshed.
- Free-space-tree loading trusts the tree structure more than the legacy loader does; it validates item sizes but does not compare parsed free space to chunk usage.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/free-space.c -->