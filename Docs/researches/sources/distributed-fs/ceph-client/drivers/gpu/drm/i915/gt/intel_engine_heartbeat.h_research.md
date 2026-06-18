<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_heartbeat.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_heartbeat.h

## Purpose
`intel_engine_heartbeat.h` declares heartbeat and barrier-flush APIs for engine liveness management.

## Important APIs, Types, and Functions
The header declares `intel_engine_init_heartbeat()`, `intel_engine_set_heartbeat()`, `intel_engine_park_heartbeat()`, `intel_engine_unpark_heartbeat()`, `intel_gt_park_heartbeats()`, `intel_gt_unpark_heartbeats()`, `intel_engine_pulse()`, and `intel_engine_flush_barriers()`.

## Control Flow
Callers initialize heartbeat work during engine PM setup, unpark/park heartbeats as engines or GTs wake/sleep, adjust intervals through the property setter, force an immediate pulse for liveness checking, and flush idle barriers by submitting a kernel request.

## State and Persistence
The header owns no state. Implementations mutate `engine->heartbeat`, engine properties, and kernel-context request state.

## Dependencies and Integration Points
Only `intel_engine_cs` and `intel_gt` are forward-declared here. The API is consumed by engine PM, sysfs/property code, hangcheck paths, and barrier management.

## Risks and Edge Cases
Callers must only pulse engines that support preemption/reset semantics, and must coordinate with engine PM so heartbeat work does not outlive initialized engine state.

## Test Signals
Build coverage for prototypes plus runtime tests for init, park/unpark, interval changes, forced pulse, and barrier flushing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_heartbeat.h -->
