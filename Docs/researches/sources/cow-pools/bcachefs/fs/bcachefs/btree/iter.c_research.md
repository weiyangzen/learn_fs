# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/iter.c

## Role

This file implements the core bcachefs btree transaction and iterator machinery. It is the main state machine for positioning btree paths, traversing from roots to nodes, peeking forward/backward/slot keys, composing staged transaction updates with on-disk btree keys, and managing `struct btree_trans` lifetime.

It sits at the center of the btree subsystem and depends on adjacent cache, locking, journal overlay, key cache, update, snapshot, and extent helpers.

## Major Responsibilities

- Maintain `struct btree_path` objects inside a transaction, including sorted ordering, refcounts, preservation, copy-on-write cloning, and lock expectations.
- Traverse btree paths root-to-leaf with restartable locking and topology checks.
- Keep node iterators valid after in-place btree node updates, key modifications, node replacement, or node drops.
- Implement public iterator operations: node iteration, forward key iteration, reverse key iteration, exact-slot lookup, root lookup, advance, rewind, and “peek and restart” wrappers.
- Merge possible key sources into iterator results: live btree nodes, current transaction updates, replay journal overlay keys, and cached keys.
- Handle snapshot filtering for btrees with snapshot fields, including whiteout behavior and saved reverse-iteration candidates.
- Allocate, initialize, recycle, and destroy btree transactions.
- Provide transaction-local bump allocation with restart-on-growth behavior.
- Emit diagnostic text for transactions, paths, updates, lock state, and leaks.

## Traversal Model

`bch2_btree_path_traverse_one()` is the main traversal engine. It ensures the transaction holds SRCU, reuses already-valid path nodes when sequence numbers still match, climbs until it finds a good ancestor, then walks down through child pointers until the requested depth is reached.

Key traversal helpers include:

- `btree_path_lock_root()` locks and validates the current btree root.
- `btree_path_down()` reads the child pointer at the current level, optionally through the journal overlay during replay, fetches the child node, updates mem-pointers, drops parent read locks when required, and initializes the next lower level.
- `btree_path_up_until_good_node()` climbs when a cached path is stale or no longer covers the requested position.
- `btree_path_prefetch()` and `btree_path_prefetch_j()` prefetch likely child nodes from ordinary btree contents or journal-overlaid contents.

Topology errors are reported by `btree_node_root_err()`, `btree_node_missing_err()`, and `btree_node_gap_err()`. These build detailed messages about broken root coverage, missing child pointers, or nodes that do not cover the expected range.

## Path Management

`bch2_path_get()` finds or creates a path for a btree ID, position, depth, lock target, and iterator flags. It reuses nearby compatible paths when possible, upgrades locks if needed, and otherwise allocates a new path slot through `btree_path_alloc()`.

Paths are sorted by btree ID, cached/non-cached state, position, and descending level. `__bch2_btree_trans_sort_paths()` uses cocktail shaker sort because paths are usually nearly sorted after small iterator moves.

Paths can be made mutable through `__bch2_btree_path_make_mut()`, which clones shared or preserved paths. Position changes go through `__bch2_btree_path_set_pos()`, which updates the path position, reuses node iterators for short forward moves, reinitializes for rewinds or large skips, and marks paths dirty when retraversal is needed.

`bch2_path_put()` releases refs, preserves duplicate paths when useful, transfers `should_be_locked` and preservation state to equivalent paths, and frees paths only when no longer required.

## Iterator Fixups

The file contains substantial logic to keep active iterators coherent while btree nodes mutate:

- `bch2_btree_path_fix_key_modified()` fixes iterators after a key’s deletedness changes.
- `bch2_btree_node_iter_fix()` adjusts node iterators after insertion/removal/replacement inside a bset and rewinds cross-bset iterator state when necessary.
- `bch2_trans_node_add()` repoints paths to a newly installed node and transfers locks.
- `bch2_trans_node_drop()` invalidates paths pointing at a dropped node.
- `bch2_trans_node_reinit_iter()` reinitializes node iterators after broad node modifications.
- `bch2_trans_revalidate_updates_in_node()` refreshes old values for transaction updates that target a modified node.

This is important because multiple transaction paths may share the same btree node at different levels.

## Forward Iteration

`__bch2_btree_iter_peek()` performs raw forward lookup from a search key. It traverses the path, peeks the current node iterator, optionally overlays key-cache entries, journal keys, and staged transaction updates, skips deleted keys, and advances to the next leaf if needed.

`bch2_btree_iter_peek_max()` wraps that with end-bound checking, snapshot filtering, whiteout filtering, update-path handling for intent iterators, transaction restart injection, and iterator position normalization. Extent iterators treat positions specially because extent keys are indexed by end position and may straddle `iter->pos`.

`bch2_btree_iter_next()` advances then peeks.

## Reverse Iteration

`__bch2_btree_iter_peek_prev()` traverses to a search key, makes the path mutable, peeks or steps backward inside the node iterator, overlays cached/journal/update keys, skips deleted keys, and moves to previous leaf nodes as needed.

`bch2_btree_iter_peek_prev_min()` adds lower-bound checks and snapshot filtering. For extents and snapshot-filtered iterators, it may use `peek_slot()` first because extent start positions are not monotonically ordered until after filtering. It also saves a candidate path when a visible ancestor snapshot key may be overwritten by a nearer snapshot key found later in the reverse scan.

`bch2_btree_iter_prev()` rewinds then peeks.

## Slot Lookup

`bch2_btree_iter_peek_slot()` returns the key at exactly `iter->pos`, synthesizing a deleted key or hole when no exact key exists. For extents and snapshot-filtered iterators, it uses a copied iterator with `BTREE_ITER_nofilter_whiteouts` and may synthesize hole extents spanning from `iter->pos` to the next key start.

`bch2_btree_path_peek_slot()` is the lower-level path form. It handles both ordinary btree leaf paths and cached key paths.

## Transaction Lifetime

`__bch2_trans_get()` allocates or reuses a transaction, attaches it to the filesystem transaction list, initializes path arrays, update arrays, lockdep state, transaction stats, SRCU state, and journal replay references.

`bch2_trans_begin()` resets a transaction for a fresh attempt or retry. It clears staged updates, reclaims unreferenced paths, drops stale replay journal references once replay finishes, handles delayed transaction memory reallocation, accounts lock-hold duration, releases locks/SRCU on long-held transactions, and retraverses paths after restart.

`bch2_trans_put()` requires no pending restart, unlocks the transaction, releases update path refs, checks leaked paths in debug builds, drops replay journal refs, releases RCU-visible transaction state, frees transaction memory, and returns the object to a per-CPU cache or mempool.

## Transaction Memory

`__bch2_trans_kmalloc()` backs transaction-local allocation. It uses an inline bump allocator in `trans->mem`, returns zeroed memory, restarts the transaction if the buffer must grow after allocations have already been made, and falls back to the transaction memory mempool if normal allocation fails.

This restart-on-growth design keeps transaction-local pointers valid within one attempt and avoids silently moving storage under active code.

## Debugging And Diagnostics

The file has extensive debug verification:

- path and node iterator invariants
- snapshot filtering correctness
- path lock coverage
- sorted path ordering
- leaked path refs
- unexpected unlocked or restarted transactions
- transaction path/update textual dumps
- per-transaction max path and max memory stats

Many invariant failures intentionally panic because corrupt iterator state can lead to btree corruption.
