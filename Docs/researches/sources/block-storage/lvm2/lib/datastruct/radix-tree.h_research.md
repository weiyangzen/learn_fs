# File Research: sources/block-storage/lvm2/lib/datastruct/radix-tree.h

## Purpose
Declares the radix-tree API used by LVM2 for byte-string keyed indexes.

## Public API
- Lifecycle: `radix_tree_create()`, `radix_tree_destroy()`.
- Mutation: `radix_tree_insert()`, `radix_tree_uniq_insert()`, `radix_tree_remove()`, `radix_tree_remove_prefix()`.
- Lookup: `radix_tree_lookup()`, `radix_tree_lookup_ptr()`.
- Traversal and collection: `radix_tree_iterate()`, `radix_tree_values()`.
- Debugging: `radix_tree_is_well_formed()`, `radix_tree_dump()`.

## Data Model
Values are stored as `union radix_value`, either `void *ptr` or `uint64_t n`. Optional destructors are called for deleted entries. Inline pointer helpers wrap the union-based calls.

## Integration
Used by bcache for `(di, block)` indexes and by dev-cache for path, devno, DM UUID, and active DM-device indexes.

## Risk Notes
The header warns that storing a `NULL` pointer is indistinguishable from lookup failure through `radix_tree_lookup_ptr()`. The documented lexicographic iteration contract is stronger than what the current implementations fully provide, especially because visitor key data is not reconstructed.
