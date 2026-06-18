# sources/distributed-fs/ceph-client/fs/btrfs/extent_map.c

## Purpose

`extent_map.c` implements the in-memory file extent map cache for Btrfs inodes. Extent maps describe logical file ranges and their corresponding on-disk extents, holes, inline data, compression, preallocation, pinning, and logging state. The file provides insertion, lookup, merging, removal, splitting, replacement, unpinning, logging cleanup, and memory-pressure shrinking.

## Important APIs, Types, And Functions

- Cache lifecycle: `btrfs_extent_map_init()` and `btrfs_extent_map_exit()` manage the `btrfs_extent_map` slab cache.
- Tree setup and object lifetime: `btrfs_extent_map_tree_init()`, `btrfs_alloc_extent_map()`, and `btrfs_free_extent_map()`.
- Internal rbtree utilities: `tree_insert()`, `tree_search()`, `lookup_extent_mapping()`, `next_extent_map()`, and `prev_extent_map()`.
- Merge logic: `can_merge_extent_map()`, `mergeable_maps()`, `merge_ondisk_extents()`, `validate_extent_map()`, and `try_merge_map()` combine adjacent safe mappings and enforce debug invariants.
- Public lookup and mutation: `btrfs_lookup_extent_mapping()`, `btrfs_search_extent_mapping()`, `btrfs_add_extent_mapping()`, `btrfs_remove_extent_mapping()`, `btrfs_drop_extent_map_range()`, `btrfs_replace_extent_map_range()`, and `btrfs_split_extent_map()`.
- State transitions: `btrfs_unpin_extent_cache()` clears pinned state after ordered extent completion and updates generation; `btrfs_clear_em_logging()` clears fast-fsync logging state and may merge.
- Shrinker: `btrfs_free_extent_maps()`, `btrfs_init_extent_map_shrinker_work()`, `btrfs_extent_map_shrinker_worker()`, `btrfs_scan_root()`, `find_first_inode_to_shrink()`, and `btrfs_scan_inode()` asynchronously drop evictable extent maps under memory pressure.

## Control Flow

Adding a mapping validates alignment and size assumptions in debug builds, inserts into the inode extent map rbtree, takes the tree reference, optionally links it into `modified_extents`, and increments `fs_info->evictable_extent_maps` for normal fs trees. If insertion collides, `btrfs_add_extent_mapping()` searches the existing nearby map. If the requested start is inside the existing map, the existing map is returned to the caller; otherwise `merge_extent_mapping()` trims the new map to the gap between neighbors and inserts that subset.

Merging is conservative. Maps cannot merge if pinned, compressed, logging, or on the modified list. Mergeable maps must be logically adjacent, have equivalent flags ignoring `EXTENT_FLAG_MERGED`, and either represent physically adjacent regular extents or matching hole/inline sentinels. Regular extent merging recomputes disk bytenr, disk length, offset, and ram bytes so a merged in-memory map can cover adjacent physical extents or different slices of the same physical extent.

Dropping a range uses two preallocated split maps for the worst case where an existing map overlaps both boundaries. It locks the extent map tree, walks intersecting maps, optionally skips pinned maps, preserves logging/modified state where needed, splits left and/or right remainders, removes covered maps, and sets full fsync on the inode if dropping an unsafely partial modified map without split memory. Replacing a range loops drop-and-add until `-EEXIST` no longer occurs.

The shrinker runs asynchronously. It records a scan target atomically, walks fs roots and inodes from saved cursor positions, uses trylocks to avoid blocking hot I/O, removes unpinned maps, marks inodes for full fsync when dropping current-generation modified maps, updates cursors, and emits tracepoints.

## State And Persistence Behavior

Extent maps are runtime cache entries and are not the on-disk source of truth. They mirror file extent items, holes, and inline data but may be merged to reduce memory. Their `generation` and `modified_extents` membership are important for fast fsync correctness. `EXTENT_FLAG_PINNED` prevents premature removal while ordered extents are not safely persisted. When dropping modified maps that may be needed by fast fsync, the code sets inode full-sync state so later fsync falls back to safer tree scanning.

The file updates `fs_info->evictable_extent_maps`, `em_shrinker_last_root`, `em_shrinker_last_ino`, and `em_shrinker_nr_to_scan`, which are runtime memory-management state. Persistent safety is protected indirectly by refusing unsafe merges/removals and by promoting inodes to full fsync when the cache can no longer support fast logging.

## Dependencies And Integration Points

This implementation depends on Linux slab, spin/rw locks, rbtrees, xarrays/radix root iteration, workqueues, percpu counters, and Btrfs inode/root/fs structures. It integrates with `btrfs_get_extent()` callers in read/write paths, ordered extent completion, fast fsync/logging, extent I/O release paths, inode eviction, memory-pressure shrinkers, tracepoints, and tests.

## Risks And Edge Cases

- Ranges use exclusive ends in many helpers but public drop uses inclusive `end`; conversion mistakes can split or remove the wrong bytes.
- Merged maps deliberately diverge from individual on-disk file extent items; code that needs exact disk item boundaries must account for `EXTENT_FLAG_MERGED`.
- Removing modified maps without preserving fast-fsync visibility can lose fsync logging unless full sync is set.
- Pinned maps must not be removed or merged; doing so can race ordered extent completion.
- The rbtree search helpers use neighbor fallback behavior; callers must distinguish strict intersection lookup from nearby search.
- Shrinker trylocks reduce latency but mean reclaim is best effort, and cursor state must remain valid across roots/inodes disappearing.

## Test Signals

Coverage should include extent-map add/lookup/drop/replace/split tests, fast fsync workloads with modified extents, ordered extent unpin paths, compression and hole/prealloc cases, memory pressure shrinker paths, debug builds for `validate_extent_map()`, tracepoint inspection, and stress with concurrent reads/writes/fsync/truncate.
