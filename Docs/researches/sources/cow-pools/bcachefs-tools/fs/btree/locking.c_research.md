# File Research: sources/cow-pools/bcachefs-tools/fs/btree/locking.c

## Purpose
`locking.c` implements bcachefs btree node/key-cache locking on top of SIX locks, transaction deadlock detection, path relock/upgrade/downgrade, transaction unlock/relock, and lock-state debug verification.

## Main Responsibilities
- Initializes btree node locks and a per-CPU lock graph used by the deadlock detector.
- Counts locks held by the current transaction on a btree node/common cached object.
- Implements cycle detection with `bch2_check_for_deadlock()`: walks transactions waiting on locks, snapshots conflicting waiters, detects cycles, chooses an abort victim, and restarts transactions to break cycles.
- Provides SIX-lock deadlock callback `bch2_six_check_for_deadlock()`, including memory-ordering barriers and stale-node reuse detection.
- Implements node lock slow paths, write-lock contention handling, and off-path locking via `bch2_btree_node_lock_with_path()`.
- Implements relock and upgrade paths: `__bch2_btree_node_relock()`, `bch2_btree_node_upgrade()`, `bch2_btree_path_relock_norestart()`, `__bch2_btree_path_relock()`, `__bch2_btree_path_upgrade_norestart()`, and `__bch2_btree_path_upgrade()`.
- Implements downgrading/unlocking: `__bch2_btree_path_downgrade()`, `bch2_trans_downgrade()`, `bch2_trans_unlock()`, `bch2_trans_unlock_long()`, and write-lock-only unlock.
- Provides lock-aware mutex acquisition (`__bch2_trans_mutex_lock()`) and debug verification for path/transaction locks.

## Important Behaviors
- SIX locks have shared, intent, and write states. Intent locks prevent upgrade deadlocks by allowing readers while serializing would-be writers.
- Deadlock detection is database-style: when a transaction would block, it follows wait edges through locks held by other transactions. On a cycle, one transaction is restarted instead of waiting indefinitely.
- Cycle detection tolerates races by revalidating frames before acting and by RCU-protecting transaction/path memory while walking wait lists.
- `bch2_six_check_for_deadlock()` checks for node reuse races before sleeping on a btree node lock; if a node identity changed, it returns a restart so traversal can be redone.
- Upgrades may update linked paths in the same transaction so restart traversal can reacquire the needed ancestor locks.
- `bch2_trans_unlock()` also releases the btree cache cannibalize lock to avoid resource deadlocks across sleeps.
- `bch2_trans_unlock_long()` drops SRCU and resets unlocked cached paths that cannot safely retain cached object pointers across SRCU release.

## Dependencies and Coupling
- Depends on `btree/locking.h` inline helpers, btree cache/node structures, SIX lock internals, wait FIFO state, transaction/path arrays from `iter.c`, btree write submission, counters, and trace events.
- Called from iterator traversal, key-cache flush/reclaim, btree update/split code, transaction wait/allocation wrappers, and debugfs-style diagnostics.

## Research Notes
- This file is the core concurrency layer for btree operations. Any investigation into transaction restarts, lock contention, unexplained latency, or path invalidation should include this file with `iter.c`.
- Memory ordering in the deadlock detector is intentional: the explicit `smp_mb()` pairs with wait-list publishing to avoid missing cycles after all participants are parked.
