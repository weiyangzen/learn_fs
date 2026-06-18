# Group Research: group_981_linux_stable_sources_os_linux_linux_stable_fs_ext4_extents_c_sources_42a75f19f557

Scope confirmed against `Docs/research_subset_a.md`: all listed files are within `sources/os/linux/linux-stable`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/extents.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/extents.c

This is ext4's core on-disk extent-tree implementation. It manages extent-tree validation, lookup, insertion, splitting, merging, deletion, block mapping/allocation, unwritten extent conversion, fallocate range operations, FIEMAP support, extent swapping, bigalloc cluster handling, and fast-commit replay repair/update helpers.

Major responsibilities:
- Extent metadata integrity: extent-block checksums via `ext4_extent_block_csum*()`, header/entry validation through `__ext4_ext_check()`, and buffer verified-bit handling around journal write access.
- Extent path lifecycle: `ext4_find_extent()` walks inode-rooted extent trees into `struct ext4_ext_path`; `ext4_free_ext_path()` and helpers release path buffer heads.
- Tree search and caching: binary searches index and leaf blocks, optionally caches discovered written/unwritten/hole mappings into the extent status tree, and supports full precache through `ext4_ext_precache()`.
- Tree mutation: `ext4_ext_insert_extent()`, `ext4_ext_split()`, `ext4_ext_grow_indepth()`, `ext4_ext_create_new_leaf()`, `ext4_ext_correct_indexes()`, and merge helpers maintain sorted, non-overlapping extent leaves and parent indexes.
- Block mapping/allocation: `ext4_ext_map_blocks()` is the main extent-backed map/create path. It handles existing initialized extents, unwritten extents, holes, bigalloc implied cluster allocation, allocator requests, insertion, cleanup on allocation/insertion failure, and map flag return semantics.
- Unwritten extent handling: split/convert helpers support buffered writes, direct I/O completion, initialized-to-unwritten conversion, zeroout fallback, and atomic write conversion.
- Truncation and punching: `ext4_ext_remove_space()`, `ext4_ext_rm_leaf()`, `ext4_remove_blocks()`, and `ext4_ext_truncate()` remove extent ranges, free blocks, update indexes, and handle bigalloc partial clusters and pending reservation rerereservation.
- Fallocate operations: `ext4_fallocate()` dispatches allocate, punch, collapse, insert, zero-range, and write-zeroes modes. Collapse/insert shift logical extents left/right after cache invalidation and journaling setup.
- FIEMAP and ES-cache reporting: `ext4_fiemap()`, xattr iomap helpers, `ext4_get_es_cache()`, and `ext4_fill_es_cache_info()` expose file and xattr layout.
- Extent swapping and replay: `ext4_swap_extents()` swaps physical mappings between locked inodes; replay helpers update extents, merge/shrink trees, recalculate `i_blocks`, and rebuild block bitmaps after fast-commit replay.

Important design points:
- The on-disk extent tree is a B-tree rooted in `EXT4_I(inode)->i_data`; depth zero means extents live directly in the inode, while deeper trees use index blocks and leaf extent blocks.
- All extent tree modifications are journaled. Metadata blocks are obtained with journal write/create access and dirtied through `ext4_ext_dirty()`.
- `i_data_sem` is the primary extent-tree mutation lock. Higher-level range operations also rely on `i_rwsem`, invalidate locking, page-cache invalidation, and DIO waits before shifting or punching mappings.
- The extent status tree is kept coherent by inserting/removing cached ranges around allocation, conversion, truncation, collapse, insert, swap, and zeroout paths. `EXT4_EX_NOCACHE` is used while extents are in flux.
- Bigalloc adds cluster-level complexity: logical/physical cluster alignment, implied allocation reuse, partial cluster states, pending reservations, and reserved-cluster rerereservation on free.
- Unwritten extents are first-class states, not holes. Reads and some lookups report them as unwritten, while writes split/convert them into initialized extents or use zeroout fallback when metadata insertion fails.
- Fast-commit replay bypasses normal journal handles in some helpers and directly adjusts extent state, then marks inode metadata dirty.

Key invariants:
- Extent headers must have the correct magic, depth, max/entry counts, and checksum when metadata checksums are enabled.
- Leaf extents and index entries must be ordered and non-overlapping.
- Extents cannot have zero length or wrap logical block space.
- Physical block ranges must pass `ext4_inode_block_valid()`.
- Parent index keys must track the first logical block in child subtrees when leaf starts change.
- Full leaves are split before inserting; root growth copies the old inode-root contents to a new metadata block and installs a single root index.
- Extent merges require matching written/unwritten state, logical adjacency, physical adjacency, and length limits.
- Partial cluster freeing is deliberately conservative to avoid freeing clusters still shared by neighboring extents.

External interfaces exported or used outside this file include extent tree initialization/release, extent lookup, path free, map blocks, truncation, fallocate, FIEMAP, extent conversion, extent swapping, cluster mapped checks, fast-commit replay helpers, and KUnit test exports.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/extents.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/extents_status.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/extents_status.c

This file implements ext4's in-memory extent status tree and the auxiliary pending cluster reservation tree. The extent status tree caches logical ranges as written, unwritten, delayed, or hole extents; it supports map lookups, FIEMAP/SEEK behavior, delayed allocation accounting, shrinker reclaim, and bigalloc reservation correctness.

Major responsibilities:
- Extent status tree lifecycle: slab creation/destruction, per-inode tree initialization, object allocation/free, per-superblock shrinker registration, and inode participation in the shrink list.
- Lookup and scanning: `ext4_es_lookup_extent()`, `ext4_es_find_extent_range()`, `ext4_es_scan_range()`, and `ext4_es_scan_clu()` search by logical block/range/cluster, using a cached recent extent before RB-tree search.
- Insert/cache/remove: `ext4_es_insert_extent()` modifies authoritative status ranges, `ext4_es_cache_extent()` only caches compatible on-disk information, and `ext4_es_remove_extent()` removes ranges while splitting edge extents when needed.
- Merging and accounting: adjacent extents with compatible status and contiguity are merged; counters track all ES objects and shrinkable ES objects.
- Reservation accounting: removal paths count delayed blocks/clusters and release delayed allocation reservations through `ext4_da_release_space()` or `ext4_da_update_reserve_space()`.
- Shrinker support: written/unwritten/hole extents are reclaimable; delayed extents are kept because FIEMAP, SEEK_DATA/SEEK_HOLE, and bigalloc accounting rely on them.
- Pending reservations: bigalloc filesystems maintain an RB-tree of logical clusters with pending reservations. Helpers insert, remove, query, and revise these entries as delayed/unwritten/written extents change.
- Debug/test support: optional aggressive consistency checks compare ES state against the on-disk extent tree or indirect block mapping.

Important design points:
- Each inode owns an `ext4_es_tree` protected by `EXT4_I(inode)->i_es_lock`.
- The tree is ordered by logical block and stores physical block plus status flags in `extent_status.es_pblk`.
- `tree->cache_es` is a single recently used extent pointer used as a fast path for common lookup and range scans.
- `ext4_es_must_keep()` currently preserves delayed extents from shrinker reclaim.
- Insertion first removes overlapping status entries, then inserts the replacement and merges with neighbors. Memory allocation failures are retried using nofail preallocation for must-keep or required operations.
- `ext4_es_cache_extent()` is intentionally weaker than `ext4_es_insert_extent()`: it refuses to overwrite conflicting existing state, except that cached holes may coexist with delayed state.
- Fast-commit replay mode bypasses most ES operations because replay rebuilds or adjusts mappings outside the normal steady-state cache rules.
- Pending reservation logic is specific to bigalloc plus delayed allocation. It avoids reading disk extents during page invalidation and protects reserved-cluster accounting when clusters mix delayed/unwritten and allocated states.

Key invariants:
- Only one of written, unwritten, delayed, or hole status types may be set at a time; referenced is an additional reclaim hint.
- RB-tree extents must not overlap and are merged when status and logical/physical adjacency allow it.
- Delayed extents are non-reclaimable.
- Shrinker-visible counters and per-superblock counters are updated whenever extents become reclaimable/non-reclaimable or are freed.
- `i_es_seq` is incremented on successful authoritative tree modifications so lookup users can detect ES changes.
- Pending reservation entries are keyed by logical cluster and are manipulated under `i_es_lock`.
- Removal accounting must not release reservations for clusters that still contain delayed blocks outside the removed range or that have pending reservations representing allocated-but-delayed-shared clusters.

External interfaces include ES initialization/teardown, insert/cache/remove/find/lookup/scan, shrinker registration and proc reporting, pending tree initialization, pending reservation insert/remove/query paths, delayed extent insertion, and clearing discretionary ES cache entries.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/extents_status.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/extents_status.h -->
# File Research: sources/os/linux/linux-stable/fs/ext4/extents_status.h

This header defines ext4's in-memory extent status API, status encoding, status-tree data structures, shrinker statistics, and pending cluster reservation interfaces.

Core definitions:
- Status bits: written, unwritten, delayed, hole, and referenced.
- `ES_SHIFT` and `ES_MASK`: reserve the high bits of `extent_status.es_pblk` for status flags while the low bits store the physical block.
- `ES_TYPE_MASK` and `ES_TYPE_VALID()`: enforce that the four extent type states are mutually exclusive.
- `struct extent_status`: RB-tree node plus logical start, length, and encoded physical block/status.
- `struct ext4_es_tree`: per-inode RB root plus one-entry recent lookup cache.
- `struct ext4_es_stats`: shrinker and cache hit/miss counters.
- `struct pending_reservation` and `struct ext4_pending_tree`: RB-tree representation of bigalloc pending cluster reservations.

Inline helpers:
- `ext4_es_status()`, `ext4_es_type()`, and type predicates classify ES entries.
- `ext4_es_is_mapped()` identifies written or unwritten mappings.
- referenced-bit helpers set/clear/query reclaim recency.
- `ext4_es_pblock()` masks out status bits to recover the physical block.
- `ext4_es_show_pblock()` formats the sentinel no-physical-block value as zero.
- `ext4_es_store_pblock()` preserves status while replacing the physical block.
- `ext4_es_store_pblock_status()` stores both physical block and a validated status type.

Public API groups:
- Extent status tree lifecycle and operations: init, insert, cache, remove, range find, lookup, scan range, scan cluster, clear inode cache.
- Shrinker lifecycle and reporting: register/unregister and seq-file info.
- Pending reservation lifecycle and operations: init, remove, query, delayed extent insertion, global init/exit.

Important constraints:
- Physical block numbers must fit below the high status bits.
- The referenced bit is not part of the mutually exclusive extent type.
- Pending reservations are only meaningful with bigalloc delayed-allocation accounting.
- The API separates authoritative modification (`ext4_es_insert_extent()`) from opportunistic caching (`ext4_es_cache_extent()`).
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/extents_status.h -->