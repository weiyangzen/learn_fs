# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-btree.c

## Purpose
Core implementation of persistent copy-on-write B+ trees with 64-bit keys, arbitrary fixed-size values, optional multi-level nested btrees, walking, lookup, insertion, and cursors.

## Main Concepts
- Node data layout is keys first, then a parallel values area sized by `header.value_size`.
- `calc_max_entries()` chooses a capacity divisible by three, supporting denser two-into-three split behavior.
- Value reference semantics are delegated to `struct dm_btree_value_type`.
- Updates are copy-on-write through `shadow_spine`.

## Major Functional Areas
- Creation/deletion:
  - `dm_btree_empty()` creates an empty leaf node.
  - `dm_btree_del()` deletes a whole tree with an explicit heap stack to avoid recursion in most of the deletion path.
- Lookup:
  - `btree_lookup_raw()` traverses with `ro_spine`.
  - `dm_btree_lookup()` supports nested btrees by iterating levels.
  - `dm_btree_lookup_next()` finds the next key after a supplied key.
- Insertion:
  - `btree_insert_raw()` shadows down to the leaf, ensures space, patches parent child pointers, and returns insertion index.
  - Full nodes may be rebalanced with siblings, split one-into-two, split two-into-three, or split beneath the root.
  - Overwrites decrement old values unless equal, then copy the new on-disk value.
  - `dm_btree_insert_notify()` reports whether the operation inserted or overwrote.
- Key discovery:
  - `dm_btree_find_lowest_key()` and `dm_btree_find_highest_key()` walk down to first/last keys.
- Walking and cursors:
  - `dm_btree_walk()` is single-level only and recursive.
  - `dm_btree_cursor_*` maintains an explicit cursor stack and can prefetch leaf-referenced blocks.

## Public API Implemented
`dm_btree_empty`, `dm_btree_del`, `dm_btree_lookup`, `dm_btree_lookup_next`, `dm_btree_insert`, `dm_btree_insert_notify`, `dm_btree_find_highest_key`, `dm_btree_find_lowest_key`, `dm_btree_walk`, `dm_btree_cursor_begin`, `dm_btree_cursor_end`, `dm_btree_cursor_next`, `dm_btree_cursor_skip`, `dm_btree_cursor_get_value`.

## Important Constraints
- `dm_btree_walk()` asserts `info->levels <= 1`.
- `btree_get_overwrite_leaf()` only works with single-level btrees and existing keys.
- Insert paths require values to be in on-disk little-endian format and annotated with the sparse disk macros.
