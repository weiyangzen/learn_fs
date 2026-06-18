# File Research: sources/block-storage/lvm2/lib/datastruct/radix-tree-adaptive.c

## Purpose
Implements LVM2's default radix tree as an adaptive radix tree with compressed prefix nodes and node fanout classes `NODE4`, `NODE16`, `NODE48`, and `NODE256`. It stores byte-string keys mapped to `union radix_value`, supports replacement, unique insert reporting, exact lookup/removal, prefix removal, iteration, debugging validation, and textual dumping.

## Main Data Structures
- `struct radix_tree` owns the root value, total entry count, and optional value destructor callback.
- `struct value` is the tagged union used at every tree position.
- `VALUE_CHAIN` represents a key that is both a complete key and a prefix of longer keys.
- `PREFIX_CHAIN` compresses a run of key bytes before a child.
- `node4`, `node16`, `node48`, and `node256` encode increasing fanout density. `node48` maps byte values through a 256-byte index table into 48 compact value slots.

## Core Behavior
Insertion first finds the longest matching prefix with `_lookup_prefix()`, then `_insert()` mutates the matching node. Inserts into `UNSET` create either a direct value or a compressed prefix chain. Inserts under an existing value create or reuse a `VALUE_CHAIN`. Diverging compressed prefixes are split, and dense nodes grow from 4 to 16 to 48 to 256 entries.

Removal walks exact key bytes, calls the configured destructor for removed values, collapses empty value chains and prefix chains, removes node entries by sliding arrays, and may shrink `NODE256` to `NODE48` or `NODE48` to `NODE16`. Prefix removal frees an entire matching subtree and decrements the global entry count by the number of destroyed values.

Lookup returns direct `VALUE` or the value stored in a `VALUE_CHAIN` when the key ends at that node. Iteration descends from a supplied prefix and calls the visitor for each stored value, but the implementation does not reconstruct keys and passes `NULL, 0` as the key arguments.

## Integration
This file is included by `radix-tree.c` unless `SIMPLE_RADIX_TREE` is defined. Device cache and bcache code use this radix tree heavily for path, devno, DM UUID, and cached-block indexes.

## Risk Notes
- Iteration callback keys are not populated despite the public API discussing ordered key traversal.
- `NODE4` and `NODE16` insertion appends keys rather than sorting them, so traversal order depends on insertion order for these nodes.
- `NODE48` iteration walks compact value slots rather than byte-key order.
- Shrink helpers can fail allocation; callers ignore the boolean result, leaving the larger node intact on failure.
- The data structure is recursive and not internally synchronized.
