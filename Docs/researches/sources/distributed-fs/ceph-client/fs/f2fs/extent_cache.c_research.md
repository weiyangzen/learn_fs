# sources/distributed-fs/ceph-client/fs/f2fs/extent_cache.c

## Purpose

`extent_cache.c` implements F2FS in-memory extent caches. It supports read extents, which map contiguous logical file offsets to contiguous physical blocks, and block-age extents, which estimate update age for hot/warm/cold data placement. The implementation provides per-inode extent trees backed by rbtrees, global radix-tree ownership, LRU-style shrink lists, largest-read-extent persistence in the inode page, and debug counters.

The file accelerates mapping lookups in `data.c`, helps fiemap and read paths avoid repeated dnode traversal, records compressed read extents when supported, and feeds block-age policy without making the cache authoritative.

## Important APIs, Types, And Functions

Core structures are `struct extent_tree_info` per cache type in `sbi`, `struct extent_tree` per inode and type, `struct extent_node` per cached range, and `struct extent_info` for the range payload. Read extents use `fofs`, `len`, `blk`, and optional compressed length `c_len`; block-age extents use `fofs`, `len`, `age`, and `last_blocks`.

Initialization and teardown APIs include `f2fs_init_extent_cache_info()`, `f2fs_create_extent_cache()`, `f2fs_destroy_extent_cache()`, `f2fs_init_read_extent_tree()`, `f2fs_init_age_extent_tree()`, `f2fs_init_extent_tree()`, `f2fs_destroy_extent_node()`, `f2fs_drop_extent_tree()`, and `f2fs_destroy_extent_tree()`.

Lookup APIs include `f2fs_lookup_read_extent_cache()`, `f2fs_lookup_read_extent_cache_block()`, and `f2fs_lookup_age_extent_cache()`, all backed by `__lookup_extent_tree()` and rb helpers.

Update APIs include `f2fs_update_read_extent_cache()`, `f2fs_update_read_extent_cache_range()`, `f2fs_update_read_extent_tree_range_compressed()`, `f2fs_update_age_extent_cache()`, and `f2fs_update_age_extent_cache_range()`, all backed by `__update_extent_cache()` or `__update_extent_tree_range()`.

Memory-pressure APIs include `f2fs_shrink_read_extent_tree()` and `f2fs_shrink_age_extent_tree()`, both backed by `__shrink_extent_tree()`.

Internal helpers include `sanity_check_extent_cache()`, `__may_extent_tree()`, `__lookup_extent_node()`, `__lookup_extent_node_ret()`, `__attach_extent_node()`, `__detach_extent_node()`, `__release_extent_node()`, `__grab_extent_tree()`, `__free_extent_tree()`, `__try_merge_extent_node()`, `__insert_extent_tree()`, `__destroy_extent_node()`, `__drop_largest_extent()`, `__calculate_block_age()`, and `__get_new_block_age()`.

## Control Flow

Extent-cache setup starts with `f2fs_init_extent_cache_info()` for each superblock and `f2fs_create_extent_cache()` for global slab caches. Per-inode trees are created lazily through `__grab_extent_tree()` when mount options and inode type allow them. Read extent initialization can seed the tree from the on-disk largest extent stored in the inode page; if the inode is not eligible, the on-disk largest extent is cleared and `FI_NO_EXTENT` is set.

Lookup enters `__lookup_extent_tree()`. It first checks whether the inode may use the requested cache. For read extents, it checks the per-tree `largest` extent before the rbtree. It then checks the cached node and rbtree, copies the matching `extent_info`, updates hit counters, moves the node to the tail of the global LRU list, and updates `cached_en`.

Range updates enter `__update_extent_tree_range()`. The function locks the per-tree rwlock, drops overlapping largest-read extent state, finds the first overlapping or neighboring node, invalidates all overlapping nodes, possibly splitting existing nodes into left and right fragments, and then inserts or merges the new extent. For read extents, a nonzero `blk` inserts a logical-to-physical mapping; a zero `blk` invalidates a range. For block-age extents, invalid ranges can remove cache state, while valid age info is merged by age similarity rather than physical contiguity.

Compressed read extent updates use `f2fs_update_read_extent_tree_range_compressed()`, which inserts a read extent with a compressed length and avoids overwriting an existing node. Merge rules prevent unsafe merging when compressed logical length differs from compressed block length.

Shrinking first tries to free zombie extent trees from evicted inodes, then removes LRU extent nodes from active trees using trylocks. Destroy paths either move still-linked inode trees to the zombie list or free all nodes and remove the tree from the radix root.

## State And Persistence Behavior

Most extent-cache state is volatile. The rbtrees, cached node pointers, LRU lists, zombie lists, counters, and block-age extents are in-memory only and can be dropped under memory pressure or inode eviction.

The exception is the largest read extent stored in the inode page (`i_ext`). `f2fs_init_read_extent_tree()` reads it at inode setup, `__try_update_largest_extent()` updates in-memory largest state, and `__update_extent_tree_range()` marks the inode dirty when the largest extent changes or is dropped. `sanity_check_extent_cache()` validates this persisted largest extent against current block-device ranges.

`FI_NO_EXTENT` is used as a persistent/inode-state guard to disable extent caching for unsuitable or fragmented cases. Small split-heavy updates can cause read extent caching to be disabled for that inode.

Block-age state tracks `allocated_data_blocks`, `last_blocks`, and weighted age. It influences policy but is not persisted in inode metadata by this file.

## Dependencies And Integration Points

`extent_cache.c` depends on F2FS inode flags, mount options (`READ_EXTENT_CACHE`, `AGE_EXTENT_CACHE`), device layout, compression feature flags, rbtrees, radix trees, slab caches, atomic counters, rwlocks, mutexes, spinlocks, and tracepoints.

Its primary consumers are `data.c` block mapping and read/write paths: `f2fs_map_blocks()` uses read extents for fast non-creating lookups and precaching; `f2fs_get_read_data_folio()` and `f2fs_do_write_data_page()` use block lookup helpers; block-address updates call `f2fs_update_read_extent_cache()`. Segment allocation and hot/cold data policy can use block-age cache information.

Debugfs statistics in `debug.c` report extent tree, zombie tree, node counts, and hit ratios using counters maintained here.

## Risks And Edge Cases

Tree mutation is complex because a single update can split, delete, merge, and insert rb nodes. The code must keep the rbtree, cached node, largest extent, per-tree node count, global node count, and LRU list synchronized. The documented release flow is list removal, rbtree detach, then slab free.

Read extents must not represent invalid physical ranges. `sanity_check_extent_cache()` rejects invalid block addresses, meta-device aliases, zoned aliases, and device-alias extents that do not exactly match any device range.

Compressed extents have special merge constraints. If compressed length differs from logical length, naive adjacency merging could create incorrect mappings, so merge checks reject those cases.

`__may_extent_tree()` intentionally disables read extent caching for writable compressed files and block-age caching for compressed or cold files. Accidentally bypassing these checks could produce stale mappings or misleading age policy.

Shrinker paths use trylocks and may leave work for later. Tests should expect partial shrink progress, not complete reclamation in one call.

## Test Signals

Good tests include repeated sequential reads to confirm read extent hits, fragmented writes to verify invalidation and `FI_NO_EXTENT` behavior, fiemap/read paths after extent precaching, compressed readonly image reads, multi-device alias validation, and memory-pressure shrinker runs.

Instrumentation should show tracepoints for lookup, update, shrink, and destroy events; debugfs should report growing and shrinking tree/node counts and plausible L1/L2 hit ratios. Corruption tests should reject invalid persisted largest extents and mark/force repair through existing F2FS error handling paths.
