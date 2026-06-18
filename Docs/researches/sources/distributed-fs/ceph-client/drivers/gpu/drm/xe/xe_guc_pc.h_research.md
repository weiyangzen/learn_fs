# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_pc.h

## Purpose
Declares the public GuC Power Conservation API.

## Important APIs, Types, And Functions
The header exposes lifecycle functions, debug printing, generic SLPC parameter operations, frequency queries and setters, power profile operations, C-state/residency queries, early init, stashed restore, unslice raise, and flush-frequency cap controls.

## Control Flow
Typical callers perform early RP initialization under forcewake, initialize the PC object, start it after GuC is ready, use frequency/profile APIs during runtime, stop on reset/suspend, and rely on managed teardown for final hardware cleanup.

## State And Persistence
State is opaque through `struct xe_guc_pc`, whose layout is in `xe_guc_pc_types.h`.

## Dependencies And Integration Points
Used by GT power management, sysfs/debugfs controls, GuC RC, reset/suspend/resume paths, and cache-flush workaround code.

## Risks And Test Signals
Callers must respect forcewake requirements for early/current FW-only reads and handle `-EAGAIN` while PC is not ready. Compile coverage plus runtime PM/frequency sysfs tests are key signals.
