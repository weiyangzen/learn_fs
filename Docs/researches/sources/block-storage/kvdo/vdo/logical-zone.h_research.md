# File Research: sources/block-storage/kvdo/vdo/logical-zone.h

## Purpose
Defines the logical-zone layer data structures and exported operations for per-logical-zone VDO write/map coordination.

## Key Structures
- `struct logical_zone`: owns per-zone completion state, LBN operation map, block map zone pointer, flush generation accounting, write VIO list, admin state, allocation selector, and ring-style `next` pointer.
- `struct logical_zones`: container for all logical zones, linked to the parent `vdo` and admin `action_manager`.

## API Surface
Exports construction/destruction, drain/resume, flush generation increment/lock acquire/release, and diagnostic dump functions:
- `vdo_make_logical_zones`
- `vdo_free_logical_zones`
- `vdo_drain_logical_zones`
- `vdo_resume_logical_zones`
- `vdo_increment_logical_zone_flush_generation`
- `vdo_acquire_flush_generation_lock`
- `vdo_release_flush_generation_lock`
- `vdo_dump_logical_zone`

## Integration Notes
The header depends on `admin-state.h`, `int-map.h`, and VDO core types. It separates logical operation tracking by LBN from physical allocation, while retaining an `allocation_selector` used to choose physical zones.

## Concurrency / State
`oldest_active_generation` is mutated only on the logical-zone thread but queried from the flusher thread, so readers must respect the implementation’s cross-thread visibility assumptions.
