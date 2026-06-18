# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map.h

## Purpose
Generic interface for persistent reference-counted space maps.

## Main Definition
`struct dm_space_map` is a function-table object that tracks block reference counts and supports transactional allocation.

## Operations
- Lifecycle: `destroy`
- Capacity: `extend`, `get_nr_blocks`, `get_nr_free`
- Refcounts: `get_count`, `count_is_more_than_one`, `set_count`, `inc_blocks`, `dec_blocks`
- Allocation: `new_block`
- Commit/root: `commit`, `root_size`, `copy_root`
- Notification: `register_threshold_callback`

## Inline Wrappers
The header provides inline wrappers such as `dm_sm_inc_block`, `dm_sm_dec_block`, `dm_sm_new_block`, and `dm_sm_copy_root`.

## Important Contract
- Newly extended space must be committed before allocation.
- Blocks free in the current transaction may not be immediately reusable if they were allocated in the previous transaction; rollback safety affects `get_nr_free()` semantics.
- `new_block()` increments the returned block’s refcount.
- Threshold callback registration is optional; wrappers return `-EINVAL` if unsupported.

## Role in Repository
This is the abstraction consumed by the transaction manager. Concrete implementations are the disk and metadata space maps.
