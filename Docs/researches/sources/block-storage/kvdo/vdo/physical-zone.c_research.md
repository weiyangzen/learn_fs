# File Research: sources/block-storage/kvdo/vdo/physical-zone.c

## Purpose
Implements physical zone construction, per-PBN lock tracking, block allocation, allocation retry across zones, and lock release.

## Construction
`vdo_make_physical_zones` allocates a flexible `physical_zones` container and initializes each zone with:
- `int_map` for PBN operations.
- fixed PBN lock pool sized at `2 * MAXIMUM_VDO_USER_VIOS`.
- zone number and thread id.
- zone-specific block allocator.
- next-zone ring pointer.
- default callback thread creation.

## Locking
- `vdo_get_physical_zone_pbn_lock`: lookup existing lock by PBN.
- `vdo_attempt_physical_zone_pbn_lock`: borrows a new lock first, attempts `int_map_put`, returns existing lock if already present, otherwise installs new lock.

## Allocation Flow
- `allocate_and_lock_block`: allocates a block, locks it, verifies it was not spuriously already held, increments holder count, assigns provisional reference.
- `vdo_allocate_block_in_zone`: returns true if allocation succeeds; otherwise tries retry/continuation handling.
- `continue_allocating`: if all zones are exhausted, optionally waits on slab scrubber; otherwise dispatches completion to next physical-zone thread.
- `retry_allocation`: restarts after clean slab wait.

## Release
`vdo_release_physical_zone_pbn_lock` decrements holder count, removes lock from map when last holder exits, releases any provisional reference, and returns lock to pool.

## Integration Notes
Connects block allocator, slab depot/scrubber, data VIO completion dispatch, int maps, PBN lock pools, and VDO thread config.
