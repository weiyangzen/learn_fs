# sources/distributed-fs/ceph-client/scripts/gdb/linux/rbtree.py

## Purpose
`rbtree.py` implements Linux RB-tree traversal helpers and GDB functions for first, last, next, and previous nodes.

## Important APIs, Types, and Functions
`rb_inorder_for_each()` recursively yields nodes in order. `rb_inorder_for_each_entry()` wraps each node with `container_of()`. `rb_first()`, `rb_last()`, `rb_parent()`, `rb_empty_node()`, `rb_next()`, and `rb_prev()` mirror kernel RB-tree helpers. GDB functions are `$lx_rb_first`, `$lx_rb_last`, `$lx_rb_next`, and `$lx_rb_prev`.

## Control Flow
First/last descend left/right from `root->rb_node`. Next/prev handle child subtrees first and then climb parent pointers encoded in `__rb_parent_color`.

## State and Persistence Behavior
Read-only. Traversal is a direct read of live memory and has no cycle protection beyond pointer semantics.

## Dependencies and Integration Points
`proc.py` and `timerlist.py` use these helpers for mount and timer RB trees. It depends on `utils.container_of()` and type caches.

## Risks and Test Signals
Corrupt trees can recurse indefinitely or produce bad pointer dereferences. `rb_prev()` returns a dereferenced node in one branch and a pointer in another, which can surprise callers. Test first/last/next/prev on empty, single-node, and multi-node trees.
