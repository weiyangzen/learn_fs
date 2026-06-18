# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_engine_activity_types.h

## Purpose
Defines the software state containers used by GuC engine activity accounting.

## Important APIs, Types, And Functions
Key types are `struct engine_activity`, `struct engine_activity_group`, `struct engine_activity_buffer`, and `struct xe_guc_engine_activity`. `engine_activity` combines accumulated driver counters with snapshots of GuC metadata and activity records. `xe_guc_engine_activity` tracks support, buffer ownership, number of functions, number of activity groups, and the GPM timestamp shift.

## Control Flow
The structures are populated by `xe_guc_engine_activity.c`: allocation creates groups and buffers, enable registers GGTT addresses with GuC, and query paths update cached fields and accumulated counters.

## State And Persistence
State persists in the embedded GuC object across stats queries. Device buffers live until managed teardown; function buffers live while per-function stats are enabled. `quanta_remainder_ns` persists to keep CPU-time scaling precise across samples.

## Dependencies And Integration Points
Includes `xe_guc_fwif.h` for firmware metadata and activity record layouts. References `struct xe_bo` without including its full definition through pointer members.

## Risks And Test Signals
The two-dimensional engine arrays must be indexed with GuC engine class and logical instance, matching the firmware layout. Tests should validate PF plus VF group sizing and that cached snapshots correctly handle unchanged GuC change numbers.
