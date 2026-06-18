# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_trace.h

## Purpose

`v3d_trace.h` defines the V3D ftrace event schema used to observe submit ioctls, hardware queue submissions, IRQ completions, CPU jobs, cache cleans, and GPU resets.

## Important APIs, Types, and Functions

- Submit ioctl events: `v3d_submit_cl_ioctl`, `v3d_submit_tfu_ioctl`, `v3d_submit_csd_ioctl`, and `v3d_submit_cpu_ioctl`.
- Hardware submit events: `v3d_submit_cl`, `v3d_submit_tfu`, and `v3d_submit_csd`.
- Completion IRQ events: `v3d_bcl_irq`, `v3d_rcl_irq`, `v3d_tfu_irq`, and `v3d_csd_irq`.
- CPU and maintenance events: `v3d_cpu_job_begin`, `v3d_cpu_job_end`, `v3d_cache_clean_begin`, `v3d_cache_clean_end`, `v3d_reset_begin`, and `v3d_reset_end`.
- `TRACE_INCLUDE_FILE v3d_trace` and final `#include <trace/define_trace.h>` integrate with the kernel tracepoint generator.

## Control Flow

Normal includers get trace prototypes through the include guard. Exactly one C file defines `CREATE_TRACE_POINTS` before including this header to instantiate the tracepoint objects. Runtime callers in submit, scheduler, IRQ, cache, and reset code invoke `trace_v3d_*` helpers generated from these definitions.

## State and Persistence Behavior

Tracepoints persist as static kernel trace event descriptors and only record when enabled by ftrace/perf tooling. Each event stores a compact snapshot such as DRM minor index, fence sequence number, CL address range, CSD CFG fields, CPU job type, or reset device index.

## Dependencies and Integration Points

The header depends on Linux tracepoint infrastructure, DRM device minor indexing, V3D job type enums, and generated trace include path handling. It is consumed directly by `v3d_trace_points.c` and referenced by scheduler, submit, IRQ, reset, and cache code.

## Risks and Edge Cases

- Event fields such as `dev->primary->index` assume a registered primary minor exists at trace time.
- Format changes affect userspace tracing scripts and kernel test expectations.
- Adding a trace event requires updating both caller code and tracepoint instantiation coverage.

## Test Signals

Build with tracing enabled, verify tracepoint generation succeeds, enable `events/v3d/*`, run CL/TFU/CSD/CPU submissions and GPU reset paths, and confirm event payloads include expected sequence numbers, job types, queue labels, and command addresses.
