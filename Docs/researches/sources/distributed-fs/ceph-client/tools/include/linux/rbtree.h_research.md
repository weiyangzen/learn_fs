<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/rbtree.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/rbtree.h

## Purpose
`rbtree.h` defines intrusive red-black tree node/root types and common insertion, lookup, cached-leftmost, replacement, and iteration helpers for tools.

## APIs And Flow
It declares `struct rb_node`, `struct rb_root`, `struct rb_root_cached`, root initializers, parent/color helpers, external balancing and traversal functions, `rb_link_node()`, `rb_entry_safe()`, postorder safe iteration, `rb_erase_init()`, cached insert/erase/replace helpers, `rb_add()`, `rb_add_cached()`, `rb_find_add()`, `rb_find()`, `rb_find_first()`, `rb_next_match()`, and `rb_for_each()`. Flow is caller-directed binary search using comparison callbacks, then link and rebalance.

## State, Dependencies, Risks, Tests
State is caller-owned tree roots and embedded rb nodes with parent/color packed into one word. Dependencies are `linux/kernel.h` and `linux/stddef.h`, plus linked rbtree implementation objects. Risks include corrupt parent/color bits, comparator partial-order ambiguity, missing locking, and unsafe postorder iteration if tree rotations occur. Tests should insert/search/delete duplicate and unique keys, cached-leftmost updates, replacement, postorder cleanup, and randomized tree invariant validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/rbtree.h -->
