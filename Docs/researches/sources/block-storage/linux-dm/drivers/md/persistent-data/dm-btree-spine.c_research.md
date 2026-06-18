# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-btree-spine.c

## Purpose
Btree node validation plus read-only and shadow spine traversal primitives.

## Main Behavior
- `btree_node_validator` validates:
  - Stored block number matches actual block location.
  - Checksum matches the node contents.
  - `max_entries` and `nr_entries` fit in the block.
  - Node is marked internal or leaf.
- `node_prepare_for_write()` stamps block number and checksum before writeback.
- `bn_read_lock()` reads a validated btree node through the transaction manager.
- `bn_shadow()` shadows a node and increments children when shadowing requires copied child references to gain references.
- `new_block()` and `unlock_block()` are small transaction-manager wrappers.

## Spine Behavior
- `ro_spine` keeps up to two read-locked nodes and drops the oldest as traversal advances.
- `shadow_spine` keeps up to two shadowed/writeable nodes and remembers the current shadow root.
- `shadow_step()` shadows a block, records the first shadow as root, and advances the rolling stack.

## Internal Value Type
`init_le64_type()` creates a btree value type for child block pointers:
- `inc` and `dec` operate on adjacent runs through `dm_tm_with_runs()`.
- `equal` compares little-endian 64-bit values.

## Role in Repository
This file isolates node validation and rolling lock mechanics, letting the higher-level btree algorithms express lookup, insertion, and removal in terms of spine steps.
