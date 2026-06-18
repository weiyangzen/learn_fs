# sources/distributed-fs/orangefs/src/io/buffer/radix.h

## Purpose
Declares radix search tree types and Linux-like wrapper functions for NCAC extent lookup.

## Important APIs, Types, And Functions
Defines `rst_node_t`, `rst_t`/`struct radix_tree_root`, radix core prototypes, inline `radix_tree_lookup`, `radix_tree_insert`, `radix_tree_delete`, `init_single_radix_tree`, and `RADIX_MAX_BITS` of 24.

## Control Flow
Callers initialize a tree with a key extractor, then insert, look up, and delete items by unsigned long index through the inline wrappers.

## State And Persistence
No global state exists. Each tree stores node pointers, traversal stacks, max key bits, and key extractor callback.

## Dependencies And Integration Points
Used by `internal.h`/`cache.c` to map inode extent indexes. Its wrapper names intentionally mimic kernel radix-tree APIs.

## Risks And Test Signals
Risks include 24-bit index limit by default, allocation hidden in initialization, and wrappers reducing duplicate insert information to `-1`. Tests should cover maximum index behavior and duplicate handling.
