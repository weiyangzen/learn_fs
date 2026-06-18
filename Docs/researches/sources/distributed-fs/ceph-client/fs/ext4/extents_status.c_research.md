# sources/distributed-fs/ceph-client/fs/ext4/extents_status.c

## Purpose

`extents_status.c` implements ext4's in-memory extent status tree. The tree tracks ranges of logical blocks and their current status: written, unwritten, delayed allocation, or hole. It is not an on-disk format; it is a cache and accounting structure used by mapping, fiemap, SEEK_DATA/SEEK_HOLE behavior, delayed allocation, writeback, and bigalloc cluster reservation logic.

The file also implements a pending-cluster reservation tree for bigalloc filesystems and a shrinker that reclaims discretionary ES entries under memory pressure. Delayed entries are mandatory and are not reclaimed because allocation, fiemap, and hole/data queries require them for correctness.

## Important APIs, types, and functions

- Lifecycle: `ext4_init_es()`, `ext4_exit_es()`, `ext4_es_init_tree()`, `ext4_clear_inode_es()`.
- Lookup and scanning: `ext4_es_lookup_extent()`, `ext4_es_find_extent_range()`, `ext4_es_scan_range()`, `ext4_es_scan_clu()`, internal `__es_find_extent_range()`, `__es_scan_range()`, `__es_scan_clu()`.
- Insertion and caching: `ext4_es_insert_extent()`, `ext4_es_cache_extent()`, `ext4_es_insert_delayed_extent()`, internal `__es_insert_extent()`.
- Removal and accounting: `ext4_es_remove_extent()`, internal `__es_remove_extent()`, `count_rsvd()`, `get_rsvd()`.
- Shrinker: `ext4_es_register_shrinker()`, `ext4_es_unregister_shrinker()`, `ext4_es_count()`, `ext4_es_scan()`, `__es_shrink()`, `es_reclaim_extents()`, `es_do_reclaim_extents()`, `ext4_seq_es_shrinker_info_show()`.
- Pending reservations: `ext4_init_pending()`, `ext4_exit_pending()`, `ext4_init_pending_tree()`, `ext4_remove_pending()`, `ext4_is_pending()`, internal `__insert_pending()`, `__remove_pending()`, `__get_pending()`, `__revise_pending()`.
- Debug/assertion support: `ext4_es_print_tree()`, `ext4_print_pending_tree()`, `ext4_es_insert_extent_check()` and its extent/indirect variants when `ES_AGGRESSIVE_TEST` is active.

## Control flow and behavior

The ES tree is a red-black tree ordered by `es_lblk`, with a one-entry `cache_es` fast path for repeated lookups. `ext4_es_lookup_extent()` first checks `cache_es`, then walks the rb-tree, returns a copied `extent_status`, optionally reports the next extent start, records the inode ES sequence, marks the live node referenced, and updates hit/miss percpu counters.

`ext4_es_insert_extent()` is the authoritative mutation interface for written/unwritten extent status. It builds a new status extent, removes overlapping entries, inserts the replacement, merges compatible neighbors, revises bigalloc pending reservations for newly allocated written/unwritten blocks, increments the ES sequence, and releases delayed allocation reservations via `ext4_da_update_reserve_space()` when delayed ranges were replaced by real allocations. It retries with nofail preallocations if splitting/removal or pending insertion initially hits memory pressure.

`ext4_es_cache_extent()` is intentionally weaker than `ext4_es_insert_extent()`. It is for caching on-disk written/unwritten/hole information only when there is no conflicting status or the existing status matches. It can remove same-status overlapping ranges and insert the cached range, but if it conflicts with delayed allocation it preserves the authoritative delayed entry and emits warnings for other conflicts. This distinction prevents read-side extent caching from accidentally converting live delayed state.

`ext4_es_insert_delayed_extent()` inserts delayed allocation ranges and, for bigalloc, records pending reservations when either edge cluster is already physically allocated. It removes overlap, inserts a delayed ES entry with `~0` physical block payload, updates pending trees, and retries with nofail allocations on memory errors. Fast-commit replay bypasses all public ES mutation and query APIs so replay can rebuild on-disk state without depending on stale in-memory cache.

`__es_remove_extent()` removes or trims a logical range. It can split a live ES node into left and right parts, remove whole rb-tree nodes, adjust physical block starts for mapped extents, reject status mismatches when a caller supplied a required status, invalidate `cache_es`, and compute how many delayed reservations should be released. Public `ext4_es_remove_extent()` wraps it with `i_es_lock`, retries with preallocated memory, increments `i_es_seq`, traces the change, and calls `ext4_da_release_space()`.

The shrinker keeps a per-superblock list of inodes with reclaimable ES entries. `ext4_es_init_extent()` adds non-mandatory entries to shrink counts and the inode list; `ext4_es_free_extent()` decrements those counters and removes the inode from the list when needed. Shrink scans skip precached inodes on the first pass, trylock inode ES locks, clear referenced bits on first encounter, and reclaim only unreferenced written/unwritten/hole entries. Delayed entries survive because `ext4_es_must_keep()` returns true for them.

Pending reservations use a second rb-tree keyed by logical cluster. `__revise_pending()` decides whether to add or remove pending reservations at edge clusters after delayed blocks become written/unwritten. `get_rsvd()` subtracts clusters that still contain delayed blocks outside the removal range and subtracts/release pending reservations for clusters whose delayed allocation should no longer consume reserved space.

## State and persistence behavior

All state in this file is in memory. It mirrors or supplements persisted extent-tree state but does not itself hit disk. Correctness depends on callers updating ES state atomically with on-disk extent mutations under `i_data_sem`, as the file header documents. ES sequence `i_es_seq` changes after successful mutations so callers can detect cache changes.

Memory state includes per-inode `i_es_tree`, `i_pending_tree`, shrink counters (`i_es_all_nr`, `i_es_shk_nr`, `i_es_shrink_lblk`), and per-superblock shrinker statistics. Physical block and status flags share `extent_status.es_pblk`; helper accessors in the header mask high bits for flags and low bits for physical block numbers.

Reservation accounting has persistent consequences even though the ES tree is transient. When delayed extents are removed or converted to real allocations, this code adjusts delayed allocation reserve counters, dirty cluster counters, quota state, and pending reservation state so later block freeing and allocation paths remain balanced.

## Dependencies and integration points

This file depends on ext4 inode/superblock private state from `ext4.h`, rb-tree APIs, slab caches, percpu counters, shrinker APIs, tracepoints, KUnit static stubs indirectly through exported test symbols, and optional debug checks that call into `ext4_find_extent()` and `ext4_ind_map_blocks()`. It integrates directly with `extents.c` through `ext4_es_cache_extent()`, `ext4_es_insert_extent()`, `ext4_es_remove_extent()`, `ext4_es_insert_delayed_extent()`, `ext4_is_pending()`, and `ext4_remove_pending()`.

Locking centers on `EXT4_I(inode)->i_es_lock`, a read/write spinlock protecting both the ES rb-tree and pending reservation tree. Superblock shrinker list state is protected by `s_es_lock`. Debug insert checks assume the caller holds `i_data_sem`, and the module-level comments define when callers must additionally hold `i_rwsem`, invalidate locks, or folio locks before querying mappings.

## Risks and edge cases

- The status tree is trusted by map-blocks paths; stale or conflicting entries can lead to wrong block mapping, reservation leaks, or incorrect hole/data reporting.
- Delayed extents are unreclaimable. A workload with many fragmented delayed ranges can grow memory use until writeback or invalidation removes them.
- `__es_insert_extent()` contains a `BUG()` for overlap insertion; callers must remove conflicting ranges first.
- `ext4_es_cache_extent()` must not be used for semantic conversion. It preserves delayed-vs-hole conflicts but warns for other mismatches, which is a useful signal of ordering bugs.
- Bigalloc reservation accounting is subtle around edge clusters, partial clusters, and pending reservations. `count_rsvd()`, `get_rsvd()`, and `__revise_pending()` must agree with `extents.c` block freeing behavior.
- Fast-commit replay explicitly bypasses the ES tree. Any replay path that later expects ES cache state must rebuild or tolerate misses.

## Test signals

Tracepoints cover lookup, insertion, delayed insertion, removal, and shrinker activity. `/proc` shrinker reporting through `ext4_seq_es_shrinker_info_show()` exposes object counts, hit/miss counters, scan time, and max inode pressure. `ES_AGGRESSIVE_TEST__` enables consistency checks against the on-disk extent tree or indirect block mapping when inserting ES entries. Useful tests should exercise delayed allocation insertion/removal, hole caching conflicts, written/unwritten conversion, cache lookup sequence tracking, shrinker reclaim of referenced and unreferenced entries, `EXT4_IOC_CLEAR_ES_CACHE`, bigalloc pending reservation insert/remove/revise paths, and fast-commit replay bypass behavior.
