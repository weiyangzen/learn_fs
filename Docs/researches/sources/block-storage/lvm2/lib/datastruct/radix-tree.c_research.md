# File Research: sources/block-storage/lvm2/lib/datastruct/radix-tree.c

## Purpose
Selects and compiles the radix-tree implementation, then adds the shared `radix_tree_values()` helper.

## Main Behavior
The file directly includes either:
- `lib/datastruct/radix-tree-simple.c` when `SIMPLE_RADIX_TREE` is defined.
- `lib/datastruct/radix-tree-adaptive.c` otherwise.

`radix_tree_values()` allocates an array sized to the tree's total entry count, iterates over the tree or prefix, and fills the array with matching values through a local visitor.

## Integration
This is the compilation unit clients link against for the public API in `radix-tree.h`. Device-cache iterators rely on `radix_tree_values()` to snapshot current device pointers before filtering.

## Risk Notes
`radix_tree_values()` allocates for all entries even when a prefix is requested, so prefix queries can overallocate. If visitor traversal stops early because the array fills, the function still returns the values collected so far.
