# Group Research: group_739_linux_sources_os_linux_linux_fs_ext4_extents_c_sources_os_linux_linu_aa78f1e53e0f

Scope: `Docs/research_subset_a.md`.

Files researched:
- `sources/os/linux/linux/fs/ext4/extents.c`
- `sources/os/linux/linux/fs/ext4/extents_status.c`
- `sources/os/linux/linux/fs/ext4/extents_status.h`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/extents.c -->
# File Research: sources/os/linux/linux/fs/ext4/extents.c

## Purpose

`extents.c` is the main ext4 extent-tree implementation. It owns on-disk extent tree validation, traversal, insertion, split/merge/growth, removal, logical-to-physical mapping, unwritten extent conversion, fallocate range operations, fiemap integration, cluster mapping queries, extent swapping, and fast-commit replay helpers.

## Major Data And State

On-disk extent tree nodes are represented by `struct ext4_extent_header`, `struct ext4_extent`, `struct ext4_extent_idx`, and `struct ext4_ext_path`. `EXT4_I(inode)->i_data` stores the root. External nodes are buffer heads in `path[i].p_bh`. `i_data_sem` protects tree structure, while the extent status tree is kept coherent through `ext4_es_cache_extent()`, `ext4_es_insert_extent()`, and `ext4_es_remove_extent()`.

## Key Behavior

`ext4_find_extent()` is the central lookup routine. It validates root depth, walks index blocks with `read_extent_tree_block()`, verifies loaded nodes, and returns the closest leaf extent for a logical block.

Insertion is handled by `ext4_ext_insert_extent()`, with helpers for index insertion, tree splitting, tree depth growth, next-leaf reuse, append/prepend merge fast paths, parent index correction, and dirtying journaled metadata.

Removal is handled by `ext4_ext_remove_space()`, which supports truncate and punch style operations. It may split the right edge first, walks right-to-left, removes leaf contents, frees empty index blocks, handles bigalloc partial clusters, and resets the tree to depth 0 when fully emptied.

`ext4_ext_map_blocks()` is the main extent-backed map/allocation path. It returns initialized mappings directly, handles unwritten conversion, reports holes for non-create lookups, allocates blocks for create requests, handles bigalloc implied cluster allocation, inserts new extents, and sets map flags such as `EXT4_MAP_NEW`, `EXT4_MAP_MAPPED`, and `EXT4_MAP_UNWRITTEN`.

## Other Responsibilities

The file implements unwritten extent conversion for buffered IO, DIO completion, atomic writes, and zero-range/write-zeroes paths. It implements fallocate allocation, punch dispatch, collapse range, insert range, and extent shifting. It also supports fiemap and ES-cache reporting, xattr fiemap mapping, extent swapping between inodes, cluster mapped queries, and fast-commit replay helpers that update extents, merge replayed trees, recompute `i_blocks`, and mark block bitmaps.

## Consistency And Risk Notes

Tree mutations assume `i_data_sem` write locking; broad range operations also rely on higher-level `i_rwsem` and invalidate locking. `EXT4_EX_NOCACHE` is used during unstable mutations to avoid corrupting ES state. Risk concentrates around split rollback, journal credit restarts that temporarily drop `i_data_sem`, unwritten zeroout fallback paths, bigalloc partial-cluster accounting, and fast-commit replay updates without normal transaction handles.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/extents.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/extents_status.c -->
# File Research: sources/os/linux/linux/fs/ext4/extents_status.c

## Purpose

`extents_status.c` implements ext4's in-memory extent status tree. It caches logical ranges as written, unwritten, delayed, or hole extents for mapping, fiemap, SEEK_DATA/SEEK_HOLE, delayed allocation, writeout, and bigalloc accounting. It also implements shrinker support and a pending cluster reservation tree for bigalloc delayed-allocation accounting.

## Core Structures

Each inode has `i_es_tree`, an RB tree ordered by logical block, plus a hot `cache_es` pointer. `i_es_lock` protects both the ES tree and pending reservation tree. Slab caches allocate `struct extent_status` and `struct pending_reservation`. Superblock state tracks shrinkable inodes and ES stats including object counts, shrink counts, cache hits/misses, and scan timings.

## Lookup And Mutation

`ext4_es_lookup_extent()` searches the hot cache then the RB tree, returns a copied ES entry, marks found entries referenced, updates hit/miss stats, and can return the next logical extent and ES sequence number.

`ext4_es_insert_extent()` is the authoritative update API for written/unwritten/hole state. It removes existing entries in the range, inserts the new entry, merges adjacent compatible entries, revises bigalloc pending reservations, and updates delayed allocation reservation accounting.

`ext4_es_cache_extent()` is cache-only. It inserts discovered on-disk state only when there is no conflicting state, allowing the special case of a cached hole conflicting with an existing delayed extent.

`ext4_es_insert_delayed_extent()` inserts delayed allocation state and pending reservations for already allocated edge clusters when needed.

`ext4_es_remove_extent()` removes a range, splits boundary entries, removes full entries, updates physical starts for right remnants, releases delayed reservations, and retries with nofail preallocations when needed.

## Shrinker And Clearing

Delayed extents are “must keep”; written, unwritten, and hole entries are reclaimable. `ext4_es_register_shrinker()` installs the shrinker. `__es_shrink()` walks inodes with shrinkable entries, skips precached inodes on the first pass, avoids lock contention, and reclaims unreferenced entries. `ext4_clear_inode_es()` removes only discretionary cache entries and preserves delayed extents.

## Pending Reservations

Pending reservations are an RB tree of logical clusters. They track bigalloc clusters where delayed/unwritten and allocated blocks share reservation/accounting state. `ext4_is_pending()` queries, `ext4_remove_pending()` removes, and `__revise_pending()` adjusts pending reservations after written/unwritten mappings replace delayed ranges.

## Consistency And Risk Notes

Most public operations no-op or report misses during fast-commit replay. Correctness depends on callers updating ES atomically with on-disk extent tree changes under `i_data_sem`, and using broader locks plus page-cache invalidation when a transaction restart can drop `i_data_sem`. Risk concentrates in partial-cluster reservation accounting, retry behavior around must-keep delayed extents, and misuse of cache-only insertion for authoritative changes.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/extents_status.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/extents_status.h -->
# File Research: sources/os/linux/linux/fs/ext4/extents_status.h

## Purpose

`extents_status.h` declares ext4's in-memory extent status tree types, status bit layout, helper accessors, and public APIs implemented by `extents_status.c`.

## Status Encoding

Status flags are packed into the high bits of `extent_status.es_pblk`. Type bits are written, unwritten, delayed, and hole; only one type bit should be set at a time. `EXTENT_STATUS_REFERENCED` is separate and is used as a shrinker aging hint. `ES_SHIFT`, `ES_MASK`, `ES_TYPE_MASK`, and `ES_TYPE_VALID()` define and validate this encoding.

## Main Types

`struct extent_status` stores an RB node, first logical block, length, and physical block plus packed status. `struct ext4_es_tree` stores the RB root and hot cached extent. `struct ext4_es_stats` stores shrinker/cache counters and timing. `struct pending_reservation` and `struct ext4_pending_tree` define bigalloc pending reservation state.

## Public APIs

The header exposes initialization and teardown for ES and pending trees, ES insert/cache/remove/find/lookup/scan APIs, shrinker registration and seq reporting, delayed extent insertion, pending reservation query/removal, and inode ES clearing.

Inline helpers decode status, test type state, test mapped state, manage the referenced bit, strip packed status from physical blocks, and store physical block plus status safely.

## Integration Notes

Callers must use helpers rather than reading `es_pblk` directly because high bits contain status. Delayed and hole extents often store placeholder physical blocks. The implementation enforces enough physical block bits with a build-time check in shrinker registration.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/extents_status.h -->