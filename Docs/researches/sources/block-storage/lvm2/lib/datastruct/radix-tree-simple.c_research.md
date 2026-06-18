# File Research: sources/block-storage/lvm2/lib/datastruct/radix-tree-simple.c

## Purpose
Provides an alternate simple radix-tree implementation selected by `SIMPLE_RADIX_TREE`. It is a ternary-search-tree-like byte trie: each node compares one byte and has `left`, `right`, and `center` children.

## Main Data Structures
- `struct node` stores one byte key, left/right alternatives, a center continuation, and an optional value.
- `struct radix_tree` stores the root node, destructor callback, destructor context, and entry count.

## Core Behavior
`radix_tree_insert()` recursively creates nodes along the key path. If a value already exists at the terminal node, the old value is destroyed and replaced; otherwise `nr_entries` is incremented.

`radix_tree_remove()` finds the terminal node, destroys its value, decrements the count, clears `has_value` if children remain, or frees the terminal node if it is a leaf. Parent cleanup is explicitly left as a FIXME.

`radix_tree_remove_prefix()` removes the exact prefix value first, then destroys the subtree reached by that prefix. Lookup uses `_lookup()` on a temporary root pointer and returns the terminal node value when present.

Iteration performs in-order traversal over left, value, center, and right branches. Like the adaptive implementation, it does not rebuild key bytes and passes `NULL, 0` to visitors.

## Integration
Included by `radix-tree.c` only when `SIMPLE_RADIX_TREE` is defined. It exists as a simpler, easier-to-reason-about implementation for comparison or debug builds.

## Risk Notes
- Removed leaf parents are not recursively pruned, so empty internal nodes can remain.
- Visitor key arguments are not populated.
- Prefix removal has subtle behavior because it removes the exact prefix value separately before destroying the looked-up subtree.
- The tree is not balanced, so adversarial key insertion order can produce deep recursion and poor lookup performance.
