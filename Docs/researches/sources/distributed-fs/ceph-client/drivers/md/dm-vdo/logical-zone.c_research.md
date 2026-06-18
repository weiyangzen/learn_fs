# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/logical-zone.c

## Purpose
`logical-zone.c` creates and manages logical zones, which serialize logical block operations, track write flush generations, coordinate zone drains/resumes, and choose physical allocation zones.

## Important APIs, Types, and Functions
Public functions are `vdo_make_logical_zones()`, `vdo_free_logical_zones()`, `vdo_drain_logical_zones()`, `vdo_resume_logical_zones()`, `vdo_increment_logical_zone_flush_generation()`, `vdo_acquire_flush_generation_lock()`, `vdo_release_flush_generation_lock()`, `vdo_get_next_allocation_zone()`, and `vdo_dump_logical_zone()`. Internals include completion conversion, action-manager zone thread lookup, per-zone initialization, admin-state drain/resume actions, oldest-generation tracking, and flusher notification callbacks.

## Control Flow
Creation allocates a flexible `logical_zones` object, initializes each zone's LBN operation map, completion, block-map-zone pointer, state, write list, allocation-zone pointer, and thread. It then creates an action manager to schedule administrative operations across zone threads. Write VIOs acquire the current flush generation and are queued on `write_vios`; release removes them and may notify the flusher when the oldest active generation advances. Drains complete only when the zone is draining, no notification is in progress, and the write list is empty. Allocation zones rotate every `ALLOCATIONS_PER_ZONE` allocations.

## State and Persistence Behavior
State is runtime-only: LBN operation maps, active write list, flush counters, notification flags, and admin states. Flush generations persist only as in-memory ordering contracts while VIOs are active; durable flush behavior is completed by the flusher and lower metadata paths.

## Dependencies and Integration Points
The file integrates with VDO action managers, admin-state machinery, block map zones, physical zones, flush subsystem, data VIO lifecycle, completions, thread configuration, `int-map`, and logging/allocation helpers.

## Risks and Edge Cases
Generation notification crosses logical-zone and flusher threads, so `oldest_active_generation` uses `READ_ONCE()` in dumps and controlled mutation on zone thread. Draining must account for in-flight notifications as well as active writes. The physical allocation-zone choice assumes physical zone count is nonzero. Thread assertions are log-only, so misuse may continue after diagnostics.

## Test Signals
Tests should cover zone creation with multiple logical/physical zones, write acquire/release ordering, flush generation increments, flusher notifications after oldest generation advances, drain waiting for active writes, resume from quiescent state, allocation-zone rotation, and dump output.
