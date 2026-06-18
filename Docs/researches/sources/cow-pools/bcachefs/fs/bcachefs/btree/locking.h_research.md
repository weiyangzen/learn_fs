# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/locking.h

This header defines the internal B-tree iterator/path locking API. It maps `six_lock` modes onto path-level state in `btree_path.nodes_locked`, tracks what locks a path wants, and provides inline helpers for lock acquisition, unlock, relock, upgrade, and verification.

Key responsibilities:
- Encodes lock state per B-tree level as unlocked/read/intent/write.
- Wraps `six_lock` operations while keeping `btree_path` bookkeeping in sync.
- Pins transactions to the current CPU and sets `PF_MEMALLOC_NOFS` while B-tree locks are held.
- Supports no-path node locking by creating temporary paths for deadlock detection and release.
- Handles write-lock downgrades/unlocks with lock sequence updates so relock validation can detect modifications.
- Exposes debug verification hooks gated by `bch2_debug_check_btree_locking`.

Important invariants:
- A write lock is represented as an intent lock plus write state; unlock of write first calls `bch2_btree_node_unlock_write`.
- Lock ordering and lock wait state feed the transaction deadlock detector.
- `path->l[level].lock_seq` must match `six_lock_seq()` when upgrading to write.
- `should_be_locked` paths cause transaction restarts if relock fails.

Dependencies include `btree/cache.h`, `btree/iter.h`, `locking_types.h`, and `util/six.h`.
