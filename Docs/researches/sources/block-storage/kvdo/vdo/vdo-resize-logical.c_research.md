# File Research: sources/block-storage/kvdo/vdo/vdo-resize-logical.c

## Purpose
Implements logical-size growth for a suspended VDO by saving the new logical block count and growing the block map.

## State Machine
Phases:
- `GROW_LOGICAL_PHASE_START`
- `GROW_LOGICAL_PHASE_GROW_BLOCK_MAP`
- `GROW_LOGICAL_PHASE_END`
- `GROW_LOGICAL_PHASE_ERROR`

All phases run on the admin thread.

## Key Functions
- `vdo_prepare_to_grow_logical()` prepares block map growth while the VDO is running.
- `vdo_perform_grow_logical()` commits the prepared logical size while the VDO is suspended.
- `grow_logical_callback()` drives the admin operation.
- `handle_growth_error()` rolls back in-memory logical block count and abandons block map growth if superblock save failed.

## Important Behavior
- No-op resume after a prepared grow abandons block map growth and succeeds.
- Growth fails with `VDO_PARAMETER_MISMATCH` if the prepared block map target does not match the requested new logical size.
- Read-only VDOs cannot grow logical size.
- The new logical size is first recorded in `states.vdo.config.logical_blocks`, saved, then the block map is grown.
