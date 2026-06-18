<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/interval_tree_generic.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/interval_tree_generic.h

## Purpose
This header is a macro template for generating interval tree insert, remove, and overlap-iteration functions over augmented red-black trees.

## APIs And Flow
`INTERVAL_TREE_DEFINE()` generates prefixed `_insert`, `_remove`, `_subtree_search`, `_iter_first`, and `_iter_next` helpers for caller-provided node type, rb-node field, interval endpoint type, subtree max field, and start/last accessors. Insert walks by start endpoint, updates ancestor subtree maxima, links the rb node, and rebalances with cached leftmost support. Search prunes by subtree maximum and leftmost start before returning overlapping intervals.

## State, Dependencies, Risks, Tests
State is caller-owned `struct rb_root_cached` plus each node's rb linkage and last-in-subtree field. It depends on `rbtree_augmented.h` and its callback macros. Risks include stale augmentation if callers mutate endpoints in place, invalid intervals where start exceeds last, and missing external locking. Tests should insert/remove overlapping and disjoint ranges, verify ordered iteration, exercise cached-leftmost fast paths, and fuzz endpoint values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/interval_tree_generic.h -->
