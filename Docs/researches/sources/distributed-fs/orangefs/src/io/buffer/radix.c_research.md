# sources/distributed-fs/orangefs/src/io/buffer/radix.c

## Purpose
Implements a standalone radix search tree used as an inode page tree for mapping extent indexes to `struct extent` pointers.

## Important APIs, Types, And Functions
Public functions are `rst_alloc`, `rst_free`, `rst_insert`, `rst_find`, `rst_delete`, and `rst_init`. Internal helpers are `rst_free_dfs`, unused `rst_find_min`, and unused `rst_finalize`.

## Control Flow
Insert traverses key bits from most significant to least, creates internal nodes only when needed to distinguish colliding key paths, and rejects duplicate keys by returning the existing item. Find traverses by key bits until reaching an item slot and validates via `get_value`. Delete records the traversal stack, removes the item, collapses unnecessary internal nodes, and returns the deleted item.

## State And Persistence
State is an in-memory tree with root node, node count, max bit depth, traversal stack, path-info stack, and `get_value` callback. No persistence exists. `rst_init` initializes an embedded tree root; `rst_alloc` creates heap-owned roots.

## Dependencies And Integration Points
`radix.h` wraps these functions with Linux-like `radix_tree_lookup/insert/delete` helpers used by NCAC inode page trees.

## Risks And Test Signals
Risks include no allocation failure checks in `rst_alloc/rst_init`, stack depth limited by `max_b`, comments noting non-commercial algorithm risk, possible `n` counter not decremented on delete, and no cleanup path for embedded trees in NCAC inodes. Tests should cover insert/find/delete for sparse keys, duplicate inserts, delete root/branch collapse cases, and allocation failure handling.
