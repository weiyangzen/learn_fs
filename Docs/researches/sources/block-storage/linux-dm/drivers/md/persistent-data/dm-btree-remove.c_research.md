# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-btree-remove.c

## Purpose
Implements single-key and range leaf removal for persistent btrees, including top-down copy-on-write rebalancing.

## Removal Strategy
The file documents the core invariant: non-root nodes should not drop below a minimum entry threshold. Before descending toward the target, child nodes are rebalanced or merged so the final removal can proceed without violating occupancy constraints while holding only a small rolling lock set.

## Main Helpers
- `node_shift`, `node_copy`, `delete_at`: low-level key/value movement inside nodes.
- `merge_threshold()`: occupancy threshold based on node capacity.
- `struct child`: shadowed child node and its index.
- `init_child()` shadows a child, increments children if required, and patches the parent pointer to the shadow.
- `rebalance2()` / `__rebalance2()`: merge or rebalance two siblings.
- `rebalance3()` / `__rebalance3()`: merge center into siblings or redistribute across three siblings.
- `rebalance_children()`: chooses root collapse, two-way rebalance, or three-way rebalance before descent.
- `remove_raw()`: shadows down the tree and prepares the target leaf for deletion.
- `remove_nearest()` and `remove_one()`: support range leaf removal.

## Public API Implemented
- `dm_btree_remove()`: removes one key path from a possibly multi-level btree and decrements the removed value through the configured value type.
- `dm_btree_remove_leaves()`: removes leaf entries in `[first_key, end_key)` and returns the count removed.

## Important Behavior
- Rebalancing happens on children of the current node, avoiding a special root case except when the root has one child, where child contents can be copied into the root.
- When merging nodes, the removed node’s block refcount is decremented without decrementing children that remain referenced after data movement.
- Parent separator keys are updated after redistribution.
- Removal returns a new root through the shadow spine.
