# sources/distributed-fs/ceph-client/include/linux/rbtree_latch.h

Purpose: implements latched red-black trees that maintain two tree copies coordinated by `seqcount_latch_t`, allowing lockless lookups even from contexts such as NMI where readers cannot retry by blocking writers.

Important APIs and types: `struct latch_tree_node` embeds two `rb_node`s. `struct latch_tree_root` stores a latch seqcount and two `rb_root`s. `struct latch_tree_ops` supplies `less` and `comp` operators. Internal helpers insert, erase, and find in one indexed tree. Public helpers are `latch_tree_insert()`, `latch_tree_erase()`, and `latch_tree_find()`.

Control flow: serialized writers update tree 0, flip the latch, update tree 1, then end the latch update so at least one tree copy is stable. Readers sample the latch sequence, search the indicated tree with RCU dereferences, and retry if the latch changed.

State and persistence: state is in-memory dual rbtrees and per-node dual links. Removed nodes must survive an RCU grace period before reuse/free.

Dependencies and integration points: depends on rbtree, seqlock latch, and RCU. It integrates ordered lookup with tracing/perf/NMI-style contexts requiring unconditional lockless access.

Risks and test signals: risks include non-serialized writers, freeing nodes before grace period, comparator inconsistency between insert and lookup, assuming iteration stability, and missing RCU read-side protection. Test concurrent insert/erase/find, NMI-like lockless lookups, duplicate-key behavior, RCU delayed free, and randomized ordering validation across both tree copies.
