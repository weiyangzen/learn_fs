# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_pc_types.h

## Purpose
Defines persistent state for GuC Power Conservation.

## Important APIs, Types, And Functions
`struct xe_guc_pc` stores the shared-data BO, flush-frequency atomic flag, fused RP0/RPn bounds, user requested min/max, stashed min/max, frequency mutex, readiness flag, and selected power profile.

## Control Flow
The implementation mutates these fields during early init, start, sysfs/debugfs frequency changes, reset recovery, flush workaround entry/exit, and final teardown.

## State And Persistence
The fields persist with the GuC object. `user_requested_*` preserve administrative intent, while `stashed_*` preserve temporary cap/unload values. `freq_ready` gates reads/writes during reset transitions.

## Dependencies And Integration Points
Includes Linux mutex/types and forward-references `struct xe_bo` through the BO pointer. The struct is embedded in `struct xe_guc`.

## Risks And Test Signals
The mutex must protect frequency limit fields except the atomic flush flag. Tests should validate no stale stashed limits remain after workaround removal or reset restore.
