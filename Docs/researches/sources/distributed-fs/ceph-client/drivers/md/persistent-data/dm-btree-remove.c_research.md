<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree-remove.c -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree-remove.c

## Purpose
Implements key removal and leaf-range removal for dm persistent btrees. It maintains btree occupancy constraints while preserving copy-on-write semantics and limiting held locks through shadow spines.

## Important APIs, Types, And Functions
The exported functions are `dm_btree_remove()` and `dm_btree_remove_leaves()`. Internal node-mutation helpers include `node_shift()`, `node_copy()`, `delete_at()`, `shift()`, `__rebalance2()`, `rebalance2()`, `delete_center_node()`, `redistribute3()`, `__rebalance3()`, `rebalance3()`, `rebalance_children()`, `remove_raw()`, `remove_nearest()`, and `remove_one()`.

`struct child` packages a shadowed child block, node pointer, and parent index. `init_child()` shadows a child and updates the parent to point at the new block, incrementing descendants if the shadow operation broke sharing.

## Control Flow
Removal descends from root to leaf using `remove_raw()`. Before stepping into a child, `rebalance_children()` ensures the child has enough entries to tolerate deletion. If the parent has one entry, the root can collapse by copying the child contents into the root. Otherwise the code rebalances two siblings when one side exists, or three siblings when both sides exist. Small combined sibling populations merge nodes and decrement removed block references; larger populations redistribute entries and update parent separator keys.

For a full key remove, `dm_btree_remove()` iterates nested btree levels, then decrements the old leaf value through the value type and deletes the key/value entry. `dm_btree_remove_leaves()` repeatedly removes the nearest leaf entry starting from `first_key` until it reaches `end_key`, updating `first_key` and counting removals.

## State And Persistence
All mutations occur on shadowed blocks returned by the transaction manager. Parent pointers are patched to new block locations after shadowing. Deleting a leaf invokes the value type's `dec` callback so referenced metadata can be freed. Merging nodes decrements metadata block references without decrementing children that remain referenced by another node.

## Dependencies And Integration Points
This file depends on internal btree helpers, transaction-manager copy-on-write and refcounts, little-endian node layout, and device-mapper error logging. Higher-level APIs in `dm-btree.h`, `dm-array`, and space-map overflow trees rely on these removal paths.

## Risks
Removal is high risk because it changes multiple siblings and parent separator keys. Off-by-one errors in shifts, merges, or `lower_bound()` handling can orphan subtrees or make keys unreachable. The code intentionally changes only top-down with limited locks; violating that convention can deadlock. `dm_btree_remove_leaves()` assumes contiguous bottom-level key semantics and callers must preserve updated `first_key`/root values.

## Test Signals
Tests should remove first, middle, last, missing, and repeated keys; force two-node and three-node rebalances; collapse root levels; remove ranges crossing leaf boundaries; use shared old roots to verify copy-on-write; and check value `dec` callbacks and metadata block refcounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree-remove.c -->
