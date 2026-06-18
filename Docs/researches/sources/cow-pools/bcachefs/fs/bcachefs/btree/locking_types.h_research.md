# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/locking_types.h

This header declares the small data structures used by the B-tree lock cycle detector.

Key types:
- `struct trans_waiting_for_lock`: records a transaction waiting for a node, desired `six_lock_type`, iteration state over held locks, and a preallocated waitlist snapshot of conflicting transactions.
- `struct lock_graph`: fixed-depth graph workspace with up to eight wait-chain entries plus a flag for whether the chain was printed.

Important behavior:
- The waitlist is cached at snapshot time so traversal is stable against concurrent wakeups.
- It carries both the node wanted and the node currently held while walking dependency chains.

Dependencies include `util/darray.h`, `util/six.h`, and `btree/types.h`.
