# Group Research: group_1660_reactos_sources_windows_reactos_drivers_filesystems_btrfs_free_spac_f32ff62e9c23

Scope: `Docs/research_subset_a.md` only. Files read completely: `sources/windows/reactos/drivers/filesystems/btrfs/free-space.c`.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/free-space.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/free-space.c

## Role

Implements WinBtrfs/ReactOS Btrfs free-space accounting for chunks. It loads free-space state from either the legacy free-space cache inode format or the free-space tree, regenerates free-space lists from the extent tree when caches are absent/invalid, persists updated free-space caches, and maintains in-memory free-space interval lists used by allocation and delayed free handling.

## Major Responsibilities

- Delete legacy cache inodes and free-space tree contents through `clear_free_space_cache()`.
- Load legacy root-tree `FREE_SPACE_ITEM` records and their cache inode payloads through `load_stored_free_space_cache()`.
- Load v2 free-space tree records from `Vcb->space_root` through `load_stored_free_space_tree()`.
- Fall back to scanning `Vcb->extent_root` for gaps when no valid cache exists.
- Protect Btrfs superblock mirror regions after loading/generating per-chunk free-space lists.
- Create or resize cache inodes for changed chunks through `allocate_cache()` / `allocate_cache_chunk()`.
- Rewrite legacy cache inode payloads through `update_chunk_cache()`.
- Rewrite free-space tree extent/info items through `update_chunk_cache_tree()`.
- Maintain interval lists with `space_list_add2()`, `space_list_subtract2()`, `space_list_add()`, and `space_list_subtract()`.

## Free-Space Models

The file maintains three related per-chunk structures:

- `c->space`: currently available free extents, ordered by address.
- `c->space_size`: the same free extents ordered by descending size for allocation heuristics.
- `c->deleting`: delayed freed ranges that should be merged into persisted free-space state but are tracked separately until commit/update.

Legacy cache support uses root-tree items keyed by `FREE_SPACE_CACHE_ID` that point to cache inodes. The cache inode payload starts with per-sector CRC32C values, a generation, and `FREE_SPACE_ENTRY` records; bitmap entries are also understood, though cache writing currently emits extents only.

Free-space tree support uses `TYPE_FREE_SPACE_INFO`, `TYPE_FREE_SPACE_EXTENT`, and `TYPE_FREE_SPACE_BITMAP` items in `Vcb->space_root`. Tree update code removes bitmap items and rewrites explicit extent items plus an info record.

## Load Path

`load_cache_chunk()` is the public idempotent loader. It calls `load_free_space_cache()`, protects superblock locations, and marks the chunk loaded.

`load_free_space_cache()` prefers the free-space tree when `BTRFS_COMPAT_RO_FLAGS_FREE_SPACE_CACHE` and `BTRFS_COMPAT_RO_FLAGS_FREE_SPACE_CACHE_VALID` are set. Otherwise it tries the legacy cache when the superblock cache generation matches. If neither source is valid, it scans extent and metadata items in the extent tree to synthesize gaps.

Legacy loading validates the cache item, opens the cache inode, rejects zero-length or too-small chunks, reads the whole inode, validates the generation and CRC32C checksums, expands extent entries and bitmap entries, checks total free space against `chunk_size - used` plus superblock-reserved space, then coalesces adjacent ranges.

Free-space tree loading reads the chunk's info item, walks following space-root items inside the chunk range, expands extent and bitmap records into intervals, then coalesces adjacent ranges.

## Persist Path

`allocate_cache()` walks changed chunks of at least 100 MiB and ensures a legacy cache inode exists with enough allocated space. `allocate_cache_chunk()` creates new cache FCBs, inserts `FREE_SPACE_ITEM` records, allocates cache extents from data chunks, or reallocates when the cache grew or its extents are on readonly/relocation chunks.

`update_chunk_cache()` copies `c->space` and `c->deleting`, merges delayed deletes, serializes all ranges as `FREE_SPACE_EXTENT` entries, updates the cache inode timestamps/generation, updates the root-tree `FREE_SPACE_ITEM`, calculates per-sector CRC32C values, and writes the cache inode. Cache write failure is intentionally nonfatal.

`update_chunk_caches()` commits legacy cache metadata and then flushes queued RAID5/RAID6 partial stripes for changed chunks.

`update_chunk_caches_tree()` marks the free-space tree valid and calls `update_chunk_cache_tree()` for changed chunks. The tree updater diffs the desired interval list against existing space-root items, inserts missing extents, deletes stale extent/bitmap items, and updates or inserts the chunk's `TYPE_FREE_SPACE_INFO`.

## Interval Operations

`add_space_entry()` inserts loaded ranges into address and size-ordered lists. `order_space_entry()` maintains descending size order.

`space_list_add2()` adds a range with overlap/adjacency coalescing and optional rollback records. `space_list_subtract2()` removes a range, including full deletion, start/end trimming, and splitting an interval around a hole. The chunk-level wrappers mark `c->changed` and `c->space_changed`; `space_list_add()` places newly freed ranges in `c->deleting`, while `space_list_subtract()` removes allocations from both active and delayed-free lists.

## Important Invariants

- `c->space` must remain sorted by address.
- `c->space_size`, when present, must contain the same nodes as `c->space` sorted by size.
- Adjacent ranges are coalesced after load and during list mutation.
- Delayed frees in `c->deleting` are merged only for persistence, not immediately into allocation-visible `c->space`.
- Cache generation and CRC validation gate use of legacy cache contents.
- Superblock mirror regions must be excluded from allocatable chunk space.
- Callers are expected to hold the appropriate chunk/global locks around most list mutations.

## Filesystem Relevance

This file is central to Btrfs allocation correctness on ReactOS/WinBtrfs. Bad free-space state can cause double allocation, leaked space, stale cache persistence, or invalid free-space tree contents. It also bridges old and new Btrfs free-space formats, so it matters for mount compatibility and post-transaction cache validity.

## Notable Risks

- Several FIXME comments call out incomplete handling for non-4096-byte sector sizes and bitmap cache writing.
- `load_free_space_bitmap()` ignores `add_space_entry()` failures, so allocation failure during bitmap expansion can silently leave incomplete free-space state.
- Some legacy-cache load error paths return after partially populating `c->space` without clearing already added entries.
- `insert_cache_extent()` appears to return success while still inside a per-chunk lock acquisition path; this depends on `insert_extent_chunk()` side effects and deserves lock-audit attention.
- `update_chunk_cache()` copies space-list nodes but does not visibly free every copied node after serialization/merge, suggesting transaction-time memory leaks.
- `update_chunk_cache_tree()` inserts `FREE_SPACE_INFO` using `sizeof(fsi)` instead of `sizeof(*fsi)` / `sizeof(FREE_SPACE_INFO)`, making the serialized size pointer-width dependent.
- Legacy cache writes are deliberately nonfatal, which is practical for degraded mounts but means cache freshness is best-effort.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/free-space.c -->