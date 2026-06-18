# File Research: sources/cow-pools/bcachefs-tools/fs/btree/locking_types.h

Read completeness: full file read, 39 lines.

Purpose: shared data structures for btree lock cycle detection. This header intentionally contains only state types, keeping the larger locking logic in `locking.h` and its implementation files.

Key definitions:
- `struct trans_waiting_for_lock` represents one transaction waiting for one node lock. It records the waiting transaction, wanted node, wanted six-lock mode, and cursor state for walking held locks.
- `waitlist` is a preallocated darray of conflicting `struct btree_trans *` entries, sized for 16 entries, used to snapshot waiter lists so recursive cycle-detection traversal is stable against concurrent wakeups.
- `struct lock_graph` is a small fixed-depth graph stack with eight `trans_waiting_for_lock` frames, a count, and a `printed_chain` diagnostic flag.

Dependencies and integration:
- Includes `util/darray.h`, `util/six.h`, and `btree/types.h`.
- Used by the per-CPU `bch2_lock_graph` declared in `locking.h`.
- The graph records `struct btree_bkey_cached_common` nodes, so it covers both btree nodes and cached bkeys that share the common lock header.

Risks and validation notes:
- The fixed graph depth is intentionally small; if future lock dependency chains become deeper, diagnostics or detection may need widening.
- `waitlist_idx`, `level`, and `path_idx` are iteration cursors and must stay consistent with the transaction path representation in `types.h`.
