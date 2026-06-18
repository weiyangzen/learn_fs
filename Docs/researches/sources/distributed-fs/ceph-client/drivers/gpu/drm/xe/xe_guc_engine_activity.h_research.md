# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_engine_activity.h

## Purpose
Declares the public GuC engine activity statistics interface.

## Important APIs, Types, And Functions
The header declares initialization, support query, device-level enable, per-function enable/disable, and active/total tick query APIs. It forward-declares `struct xe_hw_engine` and `struct xe_guc`.

## Control Flow
Callers initialize first, enable stats after GuC is ready, optionally enable per-function buffers on PFs, then query active or total ticks for a hardware engine and function ID.

## State And Persistence
The header exposes no data layout; state is owned by `struct xe_guc_engine_activity` in the types header and embedded in `struct xe_guc`.

## Dependencies And Integration Points
Used by GT accounting, SR-IOV PF telemetry, and any code that reports engine active/quanta data from GuC.

## Risks And Test Signals
The API silently returns zero for unsupported or invalid function cases through the implementation. Compile coverage plus runtime telemetry sanity checks are the key signals.
