# sources/distributed-fs/ceph-client/drivers/md/bcache/bset.c

## Purpose
`bset.c` implements operations on bcache bkeys and sorted bsets inside btree nodes: keylist management, extent trimming, auxiliary lookup-tree construction, insertion, search, iteration, sorting, and debug validation.

## Important APIs, Types, and Functions
Important routines include `bch_keylist_pop()`, `bch_keylist_pop_front()`, `bch_bkey_copy_single_ptr()`, `__bch_cut_front()`, `__bch_cut_back()`, `bch_btree_keys_alloc()`, `bch_btree_keys_free()`, `bch_bset_init_next()`, `bch_bset_build_written_tree()`, `bch_bset_fix_invalidated_key()`, `bch_bkey_try_merge()`, `bch_bset_insert()`, `bch_btree_insert_key()`, `__bch_bset_search()`, `bch_btree_iter_stack_init()`, `bch_btree_iter_next()`, `bch_btree_iter_next_filter()`, `bch_bset_sort_state_init()`, `bch_btree_sort_partial()`, `bch_btree_sort_lazy()`, `bch_btree_sort_into()`, and `bch_btree_keys_stats()`. Internal `bkey_float` nodes compress search keys for cacheline-indexed lookup trees.

## Control Flow, State, and Persistence
Written bsets get an auxiliary binary search tree indexed by one key per `BSET_CACHELINE`, using compressed mantissa/exponent values and fallback markers for ambiguous nodes. The active unwritten set uses a simpler lookup table that is updated on insert. Searches narrow to a cacheline range, then linearly scan variable-length keys. Btree iterators heap-merge multiple bsets in sorted order. Sorting merges sets into a compact output bset, optionally fixing overlapping extents and filtering invalid or stale keys depending on caller. State is held in `btree_keys`, `bset_tree`, auxiliary tree/prev arrays, and sort-state mempool pages; persistent output is the ordered bset key stream stored in btree-node memory and later written to disk.

## Dependencies and Integration Points
The file depends on `bset.h`, utility heap/mempool/time helpers, random sequence generation, prefetching, debug console output, and operation callbacks supplied by btree/extents code. It is central to btree lookup, insertion, compaction, GC, and journal replay.

## Risks and Test Signals
Risks include off-by-one errors in variable-length key walking, corrupt auxiliary tree indexes, bad extent trimming, merge logic hiding keys, mempool fallback bugs, stale-key filtering at the wrong time, and iterator heap corruption. Tests should include randomized bkey insert/search, overlapping extents, forced sort/partial sort, debug invariant checks, malformed bsets, memory allocation failure, and architecture coverage for bit arithmetic.
