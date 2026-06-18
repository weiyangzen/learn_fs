# File Research: sources/block-storage/linux-dm/drivers/md/bcache/bset.c

## Purpose
Implements manipulation of bcache bkeys and bsets: keylist growth/pop, key trimming, auxiliary search trees, bset insertion, btree-node key iteration, mergesort, lazy sorting, and bset statistics.

## Main Interfaces
- Debug helpers under `CONFIG_BCACHE_DEBUG`: `bch_dump_bset()`, `bch_dump_bucket()`, `__bch_count_data()`, `__bch_check_keys()`.
- Keylist helpers: `__bch_keylist_realloc()`, `bch_keylist_pop()`, `bch_keylist_pop_front()`.
- Key manipulation: `bch_bkey_copy_single_ptr()`, `__bch_cut_front()`, `__bch_cut_back()`.
- Btree key allocation/init: `bch_btree_keys_alloc()`, `bch_btree_keys_free()`, `bch_btree_keys_init()`.
- Bset tree and insertion: `bch_bset_init_next()`, `bch_bset_build_written_tree()`, `bch_bset_fix_invalidated_key()`, `bch_bkey_try_merge()`, `bch_bset_insert()`, `bch_btree_insert_key()`.
- Lookup/iteration/sort: `__bch_bset_search()`, `bch_btree_iter_init()`, `bch_btree_iter_next()`, `bch_btree_iter_next_filter()`, bset sort-state functions, `bch_btree_sort*()`, and `bch_btree_keys_stats()`.

## Control Flow
Written bsets get a compact auxiliary binary search tree stored as `bkey_float` records, while the current unwritten insertion set uses a simpler lookup table. Lookups first narrow to a cacheline range and then linearly scan. Insertions adjust the unwritten lookup table and may merge with adjacent keys through key-type operations. Sorting merges all active bsets through a heap iterator, optionally fixes extent overlap, drops invalid/stale keys depending on mode, and rebuilds written search trees.

## State And Synchronization
The code assumes callers hold the appropriate btree node locks. It allocates btree key pages plus auxiliary tree and previous-key arrays. Sort state uses a page mempool and time stats to keep progress under memory pressure.

## Integration Points
`btree.c` uses this for all btree node read, write, insert, split, GC, and traversal work. `extents.c` and btree pointer operations provide `btree_keys_ops` callbacks for validation, ordering, merging, and fixup.

## Notable Behaviors
- The auxiliary search tree indexes one key per 128 bytes, trading exact binary search for cache locality plus short linear scans.
- `bch_extent_sort_fixup()` callbacks can split overlapping extents during sort.
- `bch_btree_sort_lazy()` only compacts when small trailing sets or `MAX_BSETS` pressure make it worthwhile.
- Debug checks can panic on out-of-order, duplicate, or overlapping keys.

## Risks And Review Focus
- Variable-length key pointer arithmetic must stay exact.
- Search-tree compression uses fallback markers (`exponent == 127`) and is subtle.
- Insert/merge behavior depends on the specific `btree_keys_ops` implementation for extents versus interior btree pointers.
