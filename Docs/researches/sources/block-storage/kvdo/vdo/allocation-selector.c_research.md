# File Research: sources/block-storage/kvdo/vdo/allocation-selector.c

## Purpose

Implements round-robin physical-zone selection for zones that allocate data blocks.

## Main Responsibilities

- Allocates and initializes an `allocation_selector`.
- Chooses an initial physical zone from `thread_id % physical_zone_count`.
- Returns the current zone for allocation.
- Advances to the next zone after `ALLOCATIONS_PER_ZONE` allocations.

## Important Functions

- `vdo_make_allocation_selector()` allocates and initializes selector state.
- `vdo_get_next_allocation_zone()` increments allocation count and rotates zones.

## Behavior Details

Each selector uses 128 allocations per zone before rotating. If there is only one physical zone, the selector never rotates.

## Dependencies

- Uses VDO/UDS memory allocation helpers.
- Uses VDO zone and thread typedefs.
