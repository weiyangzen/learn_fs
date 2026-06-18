# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_atomic_trace.h

## Purpose
Defines ftrace trace events for MSM atomic commit phases.

## Important APIs, types, and functions
- `TRACE_EVENT(msm_atomic_commit_tail_start/finish)` records async flag and CRTC mask.
- `TRACE_EVENT(msm_atomic_async_commit_start/finish)` records the async worker CRTC mask.
- `TRACE_EVENT(msm_atomic_wait_flush_start/finish)` and `TRACE_EVENT(msm_atomic_flush_commit)` mark flush wait and issue points.
- `TRACE_SYSTEM` is `drm_msm_atomic`, with include path adjusted for generated trace code.

## Control flow
The header has declarative tracepoint definitions only. Runtime control flow is in `msm_atomic.c`, which calls the generated `trace_msm_atomic_*()` functions around commit operations.

## State and persistence
No persistent driver state. Trace records are emitted to the kernel tracing buffers when enabled.

## Dependencies and integration points
Depends on Linux tracepoint infrastructure and `msm_atomic_tracepoints.c` defining `CREATE_TRACE_POINTS`. Integrated directly by `msm_atomic.c`.

## Risks
Trace ABI names are useful for debugging and tests; renaming them can break scripts. The include guard allows multi-read for trace generation and must preserve tracepoint conventions.

## Test signals
Build coverage of trace generation and runtime visibility under `/sys/kernel/tracing/events/drm_msm_atomic/` are primary signals.
