# sources/distributed-fs/ceph-client/fs/btrfs/extent_map.h

## Purpose

`extent_map.h` defines the in-memory representation and public API for Btrfs inode extent maps. These maps cache the relationship between logical file byte ranges and disk extents, holes, inline extents, compression, preallocation, pinning, merge state, and fast-fsync logging state.

## Important APIs, Types, And Functions

- Sentinel disk bytenrs: `EXTENT_MAP_LAST_BYTE`, `EXTENT_MAP_HOLE`, and `EXTENT_MAP_INLINE` distinguish regular disk mappings from special map types.
- Flags: `EXTENT_FLAG_PINNED`, compression flags for zlib/lzo/zstd, `EXTENT_FLAG_PREALLOC`, `EXTENT_FLAG_LOGGING`, and `EXTENT_FLAG_MERGED`.
- `struct extent_map` stores the rb node, logical `start` and `len`, `disk_bytenr`, `disk_num_bytes`, logical `offset` inside the decompressed extent, `ram_bytes`, file extent `generation`, flags, refcount, and list node for modified extents.
- `struct extent_map_tree` stores the rbtree root, `modified_extents` list, and rwlock.
- Inline helpers set/query compression, test if compressed or in tree, compute block start, and compute logical map end with overflow handling.
- Public API declares tree initialization, lookup/search, add/remove/drop/replace/split, unpin, logging cleanup, allocation/free, shrinker work initialization, and shrinker triggering.

## Control Flow

Callers initialize one `extent_map_tree` per inode, allocate maps as needed while reading file extent items or creating ordered extents, fill fields according to on-disk item semantics, then add them under the tree write lock. Lookup callers use strict intersection for actual mapping and nearby search for conflict handling. Mutation callers remove, replace, split, unpin, or clear logging state as writeback, truncation, COW, and fsync progress.

The inline `btrfs_extent_map_block_start()` is important in I/O paths: compressed maps return the physical start of the compressed extent, while uncompressed maps add `offset` so the caller reaches the physical byte corresponding to the logical map start. Holes and inline extents return their sentinel.

## State And Persistence Behavior

Extent maps are transient cache, but their fields are derived from on-disk file extent items and ordered extent state. `generation`, `EXTENT_FLAG_PINNED`, `EXTENT_FLAG_LOGGING`, and `modified_extents` membership support persistence correctness by keeping fast fsync and ordered extent completion aware of extents that are not safely logged or persisted yet. `EXTENT_FLAG_MERGED` is runtime-only and tells readers the map may cover several adjacent physical/on-disk extents.

## Dependencies And Integration Points

The header depends on Linux compiler annotations, spinlock types, rbtrees, lists, refcounts, and Btrfs compression definitions. It is used by extent I/O, inode extent lookup, file write/truncate, ordered extents, fsync/log tree code, and reclaim/shrinker paths.

## Risks And Edge Cases

- The sentinel values are near `U64_MAX`; comparisons use `< EXTENT_MAP_LAST_BYTE` to distinguish regular extents. Incorrect comparisons can treat holes or inline extents as disk addresses.
- Compression flags are mutually expected by helper semantics but stored as bits; callers should not set multiple compression bits.
- `btrfs_extent_map_end()` saturates to `U64_MAX` on overflow, so range logic must be designed around exclusive end semantics.
- Struct size matters because many extent maps can be resident; adding fields has memory pressure impact.

## Test Signals

Compile coverage across Btrfs is essential. Runtime signals include extent map cache tests, compression read/write tests, hole/prealloc/inline fiemap and read tests, fast fsync tests, and memory pressure shrinker tests.
