# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/iter.h

## Role

This header exposes the bcachefs btree transaction and iterator API. It provides inline path reference helpers, traversal wrappers, lock/restart helpers, iterator initialization classes, transaction-local allocation helpers, and high-level iteration macros used throughout the filesystem.

## Major Responsibilities

- Define `bkey_err()` and `bkey_try()` helpers for iterator-returned keys.
- Manage low-level path refs with `__btree_path_get()` and `__btree_path_put()`.
- Provide path dirtying, node access, sorting, and path iteration macros.
- Expose traversal, path acquisition, path mutation, and exact-slot helpers.
- Declare lock/relock/unlock/downgrade interfaces implemented in `locking.c`.
- Define transaction restart helpers and fault-injection hook points.
- Define iterator operations for node, forward, reverse, slot, and root iteration.
- Normalize iterator flags for cached btrees, extent btrees, snapshots, and journal replay.
- Provide RAII-style `CLASS()` constructors/destructors for transactions and iterators.
- Provide restart-aware iteration macros over keys and nodes.
- Provide transaction-local allocation wrappers and lock-dropping allocation helpers.
- Provide SRCU-aware wait wrappers for closures and bit waits.

## Path And Traversal API

The header defines the fast inline wrappers that most callers use:

- `bch2_btree_path_traverse()` verifies the transaction is locked and calls the full traversal path only when the path is stale.
- `bch2_btree_path_set_pos()` avoids full repositioning when the path already has the requested position.
- `bch2_btree_path_make_mut()` clones preserved/shared paths before mutation.
- `bch2_btree_path_peek_slot_exact()` ensures cached-path lookups synthesize an exact-position missing key when the cached entry belongs to another snapshot.

Path iteration macros include unordered path scans, sorted path scans, reverse sorted scans, and “paths with this node” scans.

## Transaction Restart Model

`btree_trans_restart_ip()` records the restart reason and caller IP, and in debug builds captures a backtrace. `bch2_trans_verify_not_restarted()` checks that a retry-sensitive section did not restart unexpectedly.

`lockrestart_do()` is the standard retry loop: it calls `bch2_trans_begin()`, runs the body, verifies no hidden restart on success, and retries while the result is a transaction restart. `nested_lockrestart_do()` is a nested variant that reports `transaction_restart_nested` if the inner operation succeeded only after restarting.

These macros are central to bcachefs’s restartable btree programming model.

## Iterator Initialization

`bch2_btree_iter_flags()` derives actual iterator flags from the requested flags and btree properties:

- key cache is only enabled for cached btree IDs at leaf level
- extent mode is enabled for extent btrees unless explicitly disabled
- all-snapshot iteration is cleared for btrees without snapshot fields
- snapshot filtering is enabled for snapshot-aware btrees unless all snapshots are requested
- journal overlay is enabled while journal replay is not finished

`bch2_trans_iter_init_common()` fills `struct btree_iter` and acquires the underlying path. The header then provides outlined and inline constructors plus RAII classes for ordinary iterators, uninitialized iterators, copied iterators, and node iterators.

## Iteration Macros

The file defines restart-aware loop macros such as:

- `for_each_btree_node()`
- `for_each_btree_key()`
- `for_each_btree_key_max()`
- `for_each_btree_key_reverse()`
- commit variants that call `bch2_trans_commit()`
- no-restart variants for callers that manage restarts externally

These macros preserve the transaction model by beginning transactions, checking restart counters, advancing/rewinding iterators, and retrying on restart errors.

## Transaction Allocation Helpers

`bch2_trans_kmalloc_ip()` and `bch2_trans_kmalloc_nomemzero_ip()` allocate from transaction-local bump storage and call into `__bch2_trans_kmalloc()` when the buffer must grow. The allocation is rounded to 8 bytes, optionally traced, and reset on every `bch2_trans_begin()`.

`allocate_dropping_locks*` helpers first try nonblocking allocation and then drop transaction locks for blocking allocation. Variants either relock automatically, return an error code, or report that locks were dropped.

## Waiting And SRCU

The header contains SRCU-aware wait helpers:

- `bch2_trans_short_wait_budget()`
- `trans_closure_sync_timeout()`
- `trans_closure_sync()`
- `trans_wait_event_timeout()`
- `trans_wait_event()`
- `trans_wait_on_bit_io()`

They prevent long waits while holding the btree transaction SRCU read lock by using short wait budgets and dropping SRCU when needed.

## Public Interfaces

The header declares transaction lifecycle functions (`__bch2_trans_get()`, `bch2_trans_put()`, init/exit), iterator operations, path locking operations, transaction diagnostics, and filesystem-level btree iterator initialization/teardown.

It also provides `bch2_trans_get()` as a function-indexed macro keyed by `__func__`, enabling per-callsite transaction stats.
