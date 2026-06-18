# sources/distributed-fs/ceph-client/kernel/bpf/range_tree.c

Purpose: implements a range allocator helper used by BPF arena to track free contiguous slot ranges. It represents set bits as interval nodes and also indexes ranges by size for best-fit lookup. The source was read as a complete 262-line file.

Important APIs/functions: `range_tree_init`, `range_tree_destroy`, `range_tree_find`, `range_tree_clear`, `range_tree_set`, and `is_range_tree_set`. Important internal type: `struct range_node`, with interval-tree node, range-size rb node, start/last bounds, and subtree max field.

Control flow: `range_tree_find` walks the size-sorted rbtree for a range at least as large as requested, keeping the smallest suitable best-fit candidate by moving through the tree. `range_tree_clear` removes a range from the set by iterating overlapping interval nodes, splitting a covering node, trimming left/right overlaps, or deleting fully covered nodes. `range_tree_set` first checks if the whole range is already set, clears overlaps, finds adjacent left/right ranges, merges both, extends one side, or allocates a new node. Destroy removes all interval nodes and frees them.

State and persistence: `struct range_tree` owns two cached rb roots that reference the same `range_node` objects. Nodes persist until ranges are cleared/destroyed. External locking is required by design; the implementation does not synchronize its rb trees internally.

Dependencies/integration: uses Linux `INTERVAL_TREE_DEFINE`, rb trees, `kmalloc_nolock`/`kfree_nolock`, BPF arena users, and `range_tree.h`. Comments note the split/merge logic is based on XFS bitmap interval handling.

Risks and edge cases: `last = start + len - 1` can wrap if callers pass invalid ranges; callers must bound inputs. `start - 1` and `last + 1` adjacency probes rely on unsigned wrap semantics and valid arena limits. Allocation failure while splitting can leave earlier trimming already applied in `range_tree_clear`. External locking is mandatory.

Test signals: BPF arena allocation/free tests, best-fit range selection tests, split/merge/adjacency cases, full-range initialization/teardown, invalid/overflow range fuzzing, and KASAN/rbtree debug coverage.
