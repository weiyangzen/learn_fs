# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/locking.c

## Role

This file implements bcachefs btree node locking and transaction relocking. It uses SIX locks with shared, intent, and write states, plus a transaction-level deadlock detector that breaks cycles by restarting one transaction.

It is the locking companion to `iter.c`: iterators decide what locks they need, while this file acquires, upgrades, downgrades, releases, verifies, and deadlock-checks them.

## Major Responsibilities

- Initialize and destroy per-CPU lock graph state.
- Initialize btree node/key-cache SIX locks.
- Count locks held by a transaction on a node.
- Acquire write locks from intent locks while accounting for self-held read locks.
- Relock paths optimistically using SIX lock sequence numbers.
- Upgrade paths from read to intent locks when updates need stronger locks.
- Downgrade paths and transactions after commit or when stronger locks are no longer needed.
- Unlock transactions, including cache cannibalize lock and long-held SRCU state.
- Detect deadlock cycles among transactions waiting on btree locks.
- Abort selected transactions in a cycle by forcing transaction restart.
- Provide debug verification that path lock state matches lock expectations.

## SIX Lock Policy

The file’s documentation explains why bcachefs uses SIX locks:

- Shared locks allow ordinary readers.
- Intent locks exclude other intent lockers but coexist with shared readers.
- Write locks exclude everything and are held for short in-memory modifications.

Intent locks prevent classic read-to-write upgrade deadlocks during btree splits. Parent read locks may be dropped before taking child intent locks; sequence numbers allow optimistic relock if the node did not change.

## Deadlock Detector

`bch2_check_for_deadlock()` walks a graph of transactions blocked on locks. It starts from the current transaction’s `trans->locking`, then for each lock held by that transaction, snapshots conflicting waiters from the SIX lock wait FIFO and descends into those transactions.

Important helpers:

- `lock_graph_down()` pushes a transaction wait frame.
- `lock_graph_remove_non_waiters()` revalidates that recorded wait edges are still current.
- `lock_graph_descend()` detects cycles or recursion limit.
- `break_cycle()` selects a transaction to abort unless called only for debug cycle printing.
- `btree_trans_abort_preference()` chooses a restart victim, respecting `lock_may_not_fail`.
- `abort_lock()` either restarts the original transaction or wakes a foreign transaction with `lock_must_abort`.

The detector runs under RCU and preempt disable, uses per-frame darrays to snapshot waiters, and reports allocation failure with a dedicated restart reason instead of silently missing cycles.

## Relock And Upgrade

`__bch2_btree_node_relock()` attempts to reacquire a node lock by sequence number. It succeeds through `six_relock_type()` or by incrementing the lock when the saved sequence still matches. Failure can emit trace events.

`bch2_btree_node_upgrade()` converts a path level to intent locking. It handles already-unlocked/read/intent states, tries lock upgrade or relock, and emits trace diagnostics on failure.

`btree_path_get_locks()` walks from the path level up to `locks_want`, relocking or upgrading each node. On failure it records the failing level/node, optionally restarts the transaction, unlocks the path, marks it stale, and poisons lower levels so traversal climbs to the correct ancestor.

## Path And Transaction Locking

- `bch2_btree_path_relock_intent()` relocks intent locks for cache code and restarts on failure.
- `bch2_btree_path_relock_norestart()` tries relock without forcing restart.
- `__bch2_btree_path_relock()` restarts if relock fails.
- `__bch2_btree_path_upgrade_norestart()` and `__bch2_btree_path_upgrade()` request stronger locks.
- `__bch2_btree_path_downgrade()` lowers `locks_want`, unlocks unneeded ancestors, and downgrades intent locks to reads where possible.
- `bch2_trans_downgrade()` downgrades all referenced paths.
- `bch2_trans_relock()` reacquires all paths marked `should_be_locked`.
- `bch2_trans_unlock()` unlocks all btree paths and releases the btree-cache cannibalize lock.
- `bch2_trans_unlock_long()` additionally drops transaction SRCU and resets unlocked cached paths.

## Write Locking

`__bch2_btree_node_lock_write()` temporarily subtracts self-held read locks before taking a write lock, because SIX unlock wakeups depend on reader counts. It then restores the reader count. If the write lock fails, it restores the path as intent-locked.

`bch2_btree_node_lock_write_nofail()` wraps this and asserts success.

## Mutex Integration

`__bch2_trans_mutex_lock()` drops btree transaction locks before blocking on a regular mutex, then relocks afterward. If relock fails, it unlocks the mutex and returns the transaction restart/error result.

## Verification

`__bch2_btree_path_verify_locks()` checks that path lock state is internally consistent:

- an uptodate path with no locks must not claim `should_be_locked`
- each locked level must reference a valid btree node
- wanted lock type must match the held type, ignoring write-lock refinement where appropriate
- saved lock sequence must match the node lock sequence

`__bch2_trans_verify_locks()` checks every path when the transaction is marked locked, and asserts no path locks remain when the transaction is marked unlocked.
