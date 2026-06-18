# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_atomic_tracepoints.c

## Purpose
Instantiates the MSM atomic tracepoints declared in `msm_atomic_trace.h`.

## Important APIs, types, and functions
- Defines `CREATE_TRACE_POINTS`.
- Includes `msm_atomic_trace.h`.

## Control flow
There is no runtime logic beyond tracepoint object generation at build time.

## State and persistence
No driver state is stored here. Generated tracepoint definitions become static kernel instrumentation points.

## Dependencies and integration points
Depends entirely on Linux tracepoint build conventions and must be compiled exactly once for the trace header.

## Risks
If this file is omitted or duplicated, tracepoint linkage can fail. It must stay tiny and synchronized with the header.

## Test signals
Build/link success and available `drm_msm_atomic` trace events confirm correctness.
