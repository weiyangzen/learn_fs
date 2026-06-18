# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-disk.c

## Purpose
Implements the public `dm_space_map` interface for a general on-disk space map whose bitmap index is btree-backed.

## Main Structure
- `struct sm_disk`:
  - Embedded `struct dm_space_map sm`
  - Current low-level map `ll`
  - Previous committed map `old_ll`
  - Allocation search hint `begin`
  - `nr_allocated_this_transaction`

## Behavior
- Allocation must find a block free in both `old_ll` and current `ll`, preserving rollback safety.
- `get_nr_blocks()` reports the old committed length.
- `get_nr_free()` subtracts allocations made in the current transaction from the old committed free count.
- `set_count`, `inc_blocks`, and `dec_blocks` delegate to common low-level operations and update transaction allocation delta.
- `new_block()` searches from `begin` to the end, then wraps to `[0, begin)` if needed.
- `commit()` commits low-level index changes, snapshots current `ll` into `old_ll`, and resets transaction allocation delta.
- `copy_root()` serializes `disk_sm_root`.

## Public API Implemented
- `dm_sm_disk_create()`
- `dm_sm_disk_open()`

## Role in Repository
This is the space-map implementation suitable for general persistent structures where the index can grow via a btree.
