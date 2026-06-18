# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/interior_types.h

This header defines persistent filesystem-level state containers for btree interior node allocation reserves, in-flight interior updates, and async node rewrites.

Core responsibilities:
- Defines `struct btree_alloc`, pairing open buckets with a padded btree pointer key.
- Defines reserve sizing constants `BTREE_RESERVE_MAX` and `BTREE_NODE_RESERVE`.
- Defines `struct bch_fs_btree_reserve_cache`, a mutex-protected cache of allocated but unused btree nodes/open buckets.
- Defines `struct bch_fs_btree_interior_updates`, which owns the interior update mempool, active/unwritten lists, synchronization locks, waitlist, worker workqueue, and work item.
- Defines `struct bch_fs_btree_node_rewrites`, which tracks active and pending async rewrites/merges with a spinlock, waitlist, and worker.

Important invariants:
- The reserve cache exists to avoid livelock when btree reserve allocation fails after partially allocating nodes.
- Interior update list membership acts as a filesystem reference during async completion and shutdown synchronization.
- `commit_lock` serializes the transaction part of interior update completion with node-key updates.
- Pending node rewrites are held separately until journal replay/read-write state allows them to run.

Dependencies:
- Relies on `struct open_buckets`, padded bkey storage macros, mempools, lists, mutexes, spinlocks, closures, and workqueues defined elsewhere in bcachefs/Linux.

Risk points:
- Reserve-cache entries pin open buckets; shutdown and error paths must drain or release them.
- Active and unwritten lists must be updated under the correct mutex or flush/wait logic can miss work.
