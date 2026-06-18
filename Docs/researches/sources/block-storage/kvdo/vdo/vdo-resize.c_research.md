# File Research: sources/block-storage/kvdo/vdo/vdo-resize.c

## Purpose
Implements physical-size growth for a suspended VDO, including layout growth, recovery journal/slab summary relocation, slab depot expansion, and component-state persistence.

## State Machine
Phases:
- `GROW_PHYSICAL_PHASE_START`
- `GROW_PHYSICAL_PHASE_COPY_SUMMARY`
- `GROW_PHYSICAL_PHASE_UPDATE_COMPONENTS`
- `GROW_PHYSICAL_PHASE_USE_NEW_SLABS`
- `GROW_PHYSICAL_PHASE_END`
- `GROW_PHYSICAL_PHASE_ERROR`

All phases run on the admin thread.

## Key Functions
- `vdo_prepare_to_grow_physical()` validates that growth is allowed, prepares layout growth, and prepares slab depot growth.
- `vdo_perform_grow_physical()` commits a previously prepared physical grow while suspended.
- `grow_physical_callback()` copies old layout partitions, updates component sizes, saves metadata, activates new slabs, and updates partition pointers.
- `check_may_grow_physical()` rejects prepare when read-only or in recovery mode.
- `handle_growth_error()` routes failures into the error phase and read-only mode.

## Important Behavior
- No-op grows return success.
- Commit requires `new_physical_blocks == vdo_get_next_layout_size()`.
- Prepared slab depot size must match the next block allocator partition size.
- On mismatch, pending layout growth and new slabs are abandoned.
- On success, recovery journal and slab summary partition origins are updated after new slabs are usable.
