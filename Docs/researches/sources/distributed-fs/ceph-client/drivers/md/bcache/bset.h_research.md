# sources/distributed-fs/ceph-client/drivers/md/bcache/bset.h

## Purpose
`bset.h` declares bcache bkey and bset infrastructure. It documents the bkey model, bset layout, btree iterators, auxiliary search trees, sorting interfaces, key manipulation helpers, and debug hooks.

## Important APIs, Types, and Functions
Important types are `bset_tree`, `btree_keys_ops`, `btree_keys`, `btree_iter`, `btree_iter_stack`, `bset_sort_state`, `bset_stats`, and `keylist`. It declares APIs for btree key allocation/init/free, bset initialization and tree building, insert/merge/sort, iterator setup and advancement, keylist realloc/pop, extent cutting, pointer validity callbacks, text formatting, and debug validation.

## Control Flow, State, and Persistence
The header defines how a btree node is represented as up to `MAX_BSETS` sorted sets, with the last set optionally unwritten and mutable. It specifies search behavior: written sets use compact auxiliary trees while the unwritten set uses a lookup table; iterators merge sets with heap ordering. It also defines bkey comparison, start/end extent helpers, keylist inline storage, and size/block macros used when writing bsets to disk. Persistent behavior is indirect: these declarations govern the bset layout and bkey ordering that become on-disk btree nodes.

## Dependencies and Integration Points
It includes `bcache_ondisk.h` and `util.h` and is consumed by btree, extents, journal replay, allocator-facing key creation, debug, and GC code. The `btree_keys_ops` callbacks allow extent-specific validation, merging, and sort fixups.

## Risks and Test Signals
Risks include callback contract violations, stack iterator overflow if bsets exceed assumptions, keylist reallocation errors, incorrect filtering between invalid and bad pointers, and mismatch between macros and on-disk bset sizes. Tests should cover callback implementations, maximum bset counts, stack and mempool iterators, keylist growth, bkey cut/merge helpers, and debug builds with expensive checks enabled.
