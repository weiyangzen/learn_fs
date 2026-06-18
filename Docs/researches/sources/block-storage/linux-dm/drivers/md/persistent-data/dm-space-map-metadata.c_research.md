# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-metadata.c

## Purpose
Implements `dm_space_map` for metadata blocks, including bootstrap allocation and recursion handling needed when the space map allocates blocks for its own updates.

## Main Structures
- `struct threshold`: edge-triggered free-space threshold callback state.
- `struct block_op`: queued increment/decrement operation.
- `struct bop_ring_buffer`: fixed-size ring buffer for deferred recursive operations.
- `struct sm_metadata`: metadata space-map state, including current and old low-level maps, allocation hint, recursion count, current transaction allocations, uncommitted block ops, and threshold state.

## Recursion Handling
Metadata updates can allocate metadata blocks, which would recursively update the same space map. The file handles that with:
- `in()` / `out()` recursion-depth tracking.
- `add_bop()` to queue inc/dec operations while recursing.
- `apply_bops()` to apply queued operations when unwinding the outermost recursion.
- `combine_errors()` to preserve the first meaningful error.

## Normal Space-Map Operations
- `get_count()` and `count_is_more_than_one()` account for queued uncommitted operations.
- `set_count()` forbids recursive use.
- `inc_blocks()` and `dec_blocks()` queue when recursing or apply immediately otherwise.
- `new_block()` finds a block free in both old and current maps, increments it, tracks allocation count, and fires threshold callbacks when free space crosses the registered threshold.
- `commit()` commits low-level state, snapshots `ll` into `old_ll`, and resets transaction allocation count.
- `extend()` temporarily switches to bootstrap mode so new blocks are allocated from the extension region, then repeatedly applies bootstrap increments and commits until stable.

## Bootstrap Mode
`bootstrap_ops` is a temporary `dm_space_map` implementation used during initial creation and extension:
- Allocates linearly from `begin`.
- Treats blocks before `begin` as allocated.
- Does not support root copy, set_count, or normal extension.
- Queues inc/dec operations to be applied once the real low-level structures are ready.

## Public API Implemented
- `dm_sm_metadata_init()`
- `dm_sm_metadata_create()`
- `dm_sm_metadata_open()`

## Important Limits
- `MAX_RECURSIVE_ALLOCATIONS = 1024`
- Metadata map size is capped through `DM_SM_METADATA_MAX_BLOCKS` from the header.

## Role in Repository
This is the self-hosting allocator for device-mapper metadata blocks. It is the key piece that lets persistent-data structures allocate blocks transactionally while their allocator metadata is itself stored in persistent-data structures.
