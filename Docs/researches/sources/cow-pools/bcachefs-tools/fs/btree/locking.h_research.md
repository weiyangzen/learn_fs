# File Research: sources/cow-pools/bcachefs-tools/fs/btree/locking.h

Read completeness: full file read, 503 lines.

Purpose: inline and exported locking helpers for bcachefs btree transactions. The file bridges `struct btree_trans`, `struct btree_path`, `struct btree_bkey_cached_common`, and the six-lock implementation, so iterator traversal code can record which node locks are held or wanted and can restart safely on contention or invalidation.

Key definitions:
- `enum btree_node_locked_type` maps btree path lock state onto six-lock read, intent, and write modes, plus `BTREE_NODE_UNLOCKED`.
- `trans_set_locked()` and `trans_set_unlocked()` wrap transaction lockdep state, pin execution to the current CPU while btree locks are held, and set `PF_MEMALLOC_NOFS` to avoid filesystem recursion during memory allocation.
- `btree_node_locked_type()`, `btree_node_*_locked()`, `mark_btree_node_locked*()`, `btree_lock_want()`, and level helpers encode per-level lock state into `path->nodes_locked`.
- Unlock helpers include `bch2_btree_node_unlock_write_inlined()`, `btree_node_unlock()`, `__bch2_btree_path_unlock()`, and `bch2_btree_node_unlock_with_path()`.
- Lock helpers include `btree_node_lock_nopath()`, `btree_node_lock()`, `__btree_node_lock_write()`, `bch2_btree_node_lock_write()`, `bch2_btree_node_lock_write_nofail()`, and `bch2_btree_node_lock_with_path()`.
- Relock and upgrade surface: `bch2_btree_path_relock()`, `bch2_btree_node_relock()`, `bch2_btree_node_relock_notrace()`, `bch2_btree_path_upgrade_norestart()`, and `bch2_btree_path_upgrade()`.

Control-flow and invariants:
- `bch2_btree_path_traverse()` refuses to traverse from an unlocked/restarting transaction and only calls the slow traversal path when no nodes are locked.
- Write-lock acquisition intentionally marks the path as write-locked before trying `six_trylock_write()`, because the deadlock detector must know this transaction is trying to block readers behind a pending write lock.
- Unlocking a write lock first downgrades transaction-visible state to intent, advances linked path lock sequence numbers when recursion is not active, then releases the six write lock.
- Relock helpers compare desired lock mode against saved path state and lock sequence values so stale paths restart rather than using reclaimed or modified nodes.
- `btree_path_set_should_be_locked()` records that a path must relock successfully or force a transaction restart.

Dependencies and integration:
- Depends on `btree/cache.h`, `btree/iter.h`, `btree/locking_types.h`, and `util/six.h`.
- Uses `struct btree_trans` and `struct btree_path` fields defined in `types.h`.
- Calls out to slow paths and diagnostics implemented elsewhere: `bch2_btree_node_lock_slowpath()`, `bch2_btree_node_lock_write_contended()`, `bch2_six_check_for_deadlock()`, `bch2_check_for_deadlock()`, and lock verification helpers.
- Interacts with write code through `bch2_btree_node_unlock_write()` and with traversal/update code through path relock, upgrade, and should-be-locked state.

Risks and validation notes:
- `nodes_locked` packs two bits per level; any new lock type or depth change must preserve the encoding assumptions and `BUILD_BUG_ON()` checks.
- Transaction code relies on CPU migration and `PF_MEMALLOC_NOFS` being restored exactly once in `trans_set_unlocked()`.
- Deadlock detection depends on callers setting `trans->locking_hash_val` before `btree_node_lock_nopath()` when the lock is looked up by hash.
- Debug coverage is mostly compile-time and runtime assert based: `EBUG_ON`, lockdep, event traces, optional lock time stats, and `bch2_trans_verify_locks()`.
