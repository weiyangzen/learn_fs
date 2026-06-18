# sources/distributed-fs/ceph-client/include/linux/rculist_bl.h

Purpose: supplies RCU traversal and mutation helpers for bit-lock hash lists (`hlist_bl`), whose head pointer stores a lock bit in the low address bit.

Important APIs and types: `hlist_bl_first_rcu()` and `hlist_bl_next_rcu()` expose RCU pointers. `hlist_bl_set_first_rcu()` publishes a first node while preserving the lock bit. `hlist_bl_first_rcu_dereference()` masks the lock bit after checked dereference. Mutators include `hlist_bl_del_rcu()` and `hlist_bl_add_head_rcu()`. Traversal macros include `hlist_bl_for_each_entry_rcu()` and continue variant.

Control flow: writers hold the bucket bit-lock, add or delete nodes, and publish first-node changes with RCU assignment because readers may traverse locklessly. Readers dereference the first node with lock-aware checks, mask out the lock bit, and continue through RCU next pointers.

State and persistence: state is caller-owned `hlist_bl_head`/node memory with low-bit lock encoding. Deleted nodes must not be freed until readers drain.

Dependencies and integration points: depends on `list_bl.h` and RCU. It is used by hash tables needing compact per-bucket locking plus RCU read-side lookup.

Risks and test signals: risks include losing or misinterpreting the lock bit, unaligned node pointers, freeing nodes too early, traversing without RCU protection, and writer updates without the bit-lock. Test bucket lock/unlock with concurrent lookups, add/delete races, lock-bit masking, hash table resize/teardown, and debug list checks.
