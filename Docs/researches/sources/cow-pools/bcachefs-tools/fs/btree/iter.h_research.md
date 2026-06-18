# File Research: sources/cow-pools/bcachefs-tools/fs/btree/iter.h

## Purpose
`iter.h` is the public/internal interface for bcachefs btree transactions, iterators, path helpers, restart loops, transaction-local allocation, and iterator convenience macros.

## Main Responsibilities
- Declares path and transaction diagnostic helpers such as `bch2_trans_paths_to_text()`, `bch2_dump_trans_paths_updates()`, and `bch2_btree_trans_to_text()`.
- Provides inline path reference management (`__btree_path_get()`, `__btree_path_put()`), sorted path iteration macros, and helpers for walking paths with a specific btree node.
- Declares path operations: make mutable, set position, traverse one path, get/release paths, peek exact slots, relock/upgrade/downgrade, node fixups, and transaction node update hooks.
- Declares iterator operations and implements small inline wrappers for `peek`, `peek_prev`, position setting, snapshot setting, common initialization, and RAII-style `CLASS()` wrappers.
- Defines `bch2_btree_iter_flags()`, which normalizes caller flags based on btree type, level, snapshot support, cache eligibility, extent semantics, and journal replay state.
- Provides restart and loop macros: `lockrestart_do()`, `nested_lockrestart_do()`, `for_each_btree_key*`, reverse iteration variants, commit variants, and no-restart variants.
- Provides transaction wait/allocation wrappers that know how to drop SRCU before long waits and how to drop/relock btree locks around blocking allocation.

## Important Behaviors
- Cached btree IDs are restricted to alloc, inodes, logged ops, and subvolumes. Leaf iterators over these can automatically use the key cache unless explicitly cached already.
- `bch2_trans_iter_init()` exits any existing iterator before initializing it; uninitialized/copy/node iterator classes wrap common cleanup.
- `bch2_btree_iter_set_pos()` also drops any `update_path`, because a saved update path is only valid for the previous iterator position.
- `lockrestart_do()` is a loop-form macro so cleanup attributes inside the body run on each retry.
- `drop_locks_do()` and allocation helpers are intentionally warned as not fast-path friendly unless a nonblocking attempt has already failed.

## Dependencies and Coupling
- Includes btree node/cache types, closure APIs, and counters.
- References functions implemented across `iter.c`, `locking.c`, `key_cache.c`, and update/commit code.
- Macro users throughout bcachefs depend on these exact restart semantics and cleanup behavior.

## Research Notes
- This header encodes much of the btree API contract. Research into call sites should treat iterator flags as part of behavior, not as minor options.
- The wait helpers are notable for SRCU memory-reclaim safety: code with a `btree_trans` in scope should use these wrappers instead of raw closure waits or bit waits when waits may be long.
