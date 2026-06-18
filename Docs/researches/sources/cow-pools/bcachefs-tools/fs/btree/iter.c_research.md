# File Research: sources/cow-pools/bcachefs-tools/fs/btree/iter.c

## Purpose
`iter.c` is the core bcachefs btree transaction and iterator implementation. It owns path allocation, path traversal from root to leaf, iterator peek/next/prev/slot semantics, transaction restart handling, transaction-local allocation, diagnostics, and filesystem-level transaction iterator initialization/teardown. The opening documentation frames the API around transaction-scoped btree iterators rather than one-off lookups.

## Main Responsibilities
- Maintains `struct btree_path` invariants: sorted transaction path list, reference and intent reference counts, preserved paths, lock state, cached vs real btree paths, and path position consistency with per-node iterators.
- Traverses paths down the btree with `bch2_btree_path_traverse_one()`, using root locking, child pointer lookup, topology checks, optional prefetch, journal overlay during replay, and recovery from stale or invalid cached levels.
- Exposes iterator operations: `bch2_btree_iter_peek_max()`, `bch2_btree_iter_next()`, `bch2_btree_iter_peek_prev_min()`, `bch2_btree_iter_prev()`, `bch2_btree_iter_peek_slot()`, slot next/prev, node iteration, and root-key peeking.
- Merges visible candidates from the on-disk btree, the journal overlay, transaction-local staged updates, and the btree key cache.
- Handles snapshot-aware filtering. Forward scans use `btree_iter_filter_snapshots()` to skip unrelated snapshot branches and whiteouts while maintaining monotonic progress; reverse scans keep a saved candidate path while searching for same-position overwrites.
- Provides path repair after btree mutation: `bch2_btree_path_fix_key_modified()`, `bch2_btree_node_iter_fix()`, `bch2_trans_node_add()`, `bch2_trans_node_reinit_iter()`, and update revalidation in modified nodes.
- Owns transaction lifecycle: `bch2_trans_begin()`, `__bch2_trans_get()`, `bch2_trans_put()`, transaction path cleanup, SRCU handling, mempool/per-CPU transaction reuse, and transaction stats.

## Important Behaviors
- Extent iterators are special: search keys use the successor of `iter->pos`, returned extents may straddle `iter->pos`, and `peek_slot()` synthesizes hole keys so slot iteration covers keyspace.
- `BTREE_ITER_all_snapshots`, `BTREE_ITER_filter_snapshots`, `BTREE_ITER_snapshot_field`, and `BTREE_ITER_is_extents` materially change ordering and position semantics.
- `bch2_path_get()` reuses compatible existing paths when possible, otherwise allocates and inserts a new sorted path. Path sorting uses a cocktail-shaker pass because paths are usually nearly sorted.
- Transaction restarts are represented by `trans->restarted`; callers use `bch2_trans_begin()`/`lockrestart_do()` patterns to reset transient state and retry.
- `__bch2_trans_kmalloc()` is a per-transaction bump allocator. Growth after an allocation exists triggers a transaction restart so callers retry with a larger buffer.
- During journal replay, long-lived transactions hold a journal-key reference and automatically drop it after replay completes on a later `bch2_trans_begin()`.

## Dependencies and Coupling
- Heavily coupled to `btree/locking.h` and `locking.c` for relock, upgrade, unlock, and deadlock-restart behavior.
- Calls into `journal_overlay.c` for replay-time journal-key peeking and btree-plus-journal child lookup.
- Integrates with `key_cache.c` for cached single-key paths and cached key lookups.
- Depends on btree node iterator primitives from `btree/bset.h`/cache/interior code, bkey packing/unpacking helpers, snapshot ancestry checks, journal validation/text helpers, and transaction commit/update paths.

## Research Notes
- This file is a central correctness choke point: path position, iterator cursor, lock state, journal overlay state, and transaction-local updates must stay mutually consistent.
- There is an explicit TODO/comment around reverse iteration: `peek_prev` may leave `path->pos` inconsistent with ancestor levels because it does not normalize with a trailing `set_pos()` like forward peeking. That is likely relevant for restart/fault-injection or node-split investigations.
- Debug-only verification is extensive but often static-branch gated; release behavior relies on the same invariants without continuous checking.
