# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gpu_tracepoints.c

## Purpose
Instantiates the tracepoints declared in `msm_gpu_trace.h` by defining `CREATE_TRACE_POINTS` in exactly one translation unit.

## Important APIs, Types, and Functions
The file includes `msm_gem.h`, `msm_ringbuffer.h`, defines `CREATE_TRACE_POINTS`, and includes `msm_gpu_trace.h`. It has no functions of its own.

## Control Flow
No runtime control flow. During compilation, tracepoint macros emit the storage and registration metadata for all `drm_msm_gpu` events.

## State and Persistence
The generated tracepoint descriptors are kernel static state. There is no driver-specific mutable state in this file.

## Dependencies and Integration Points
Must include the data-structure headers needed by tracepoint field assignments before including `msm_gpu_trace.h`. Other files include `msm_gpu_trace.h` without `CREATE_TRACE_POINTS` and call the generated trace helpers.

## Risks
Defining `CREATE_TRACE_POINTS` in multiple files would cause duplicate definitions; omitting this file would leave tracepoints unresolved. Include ordering can break if tracepoint expressions require incomplete types.

## Test Signals
Successful module/kernel link and visible `drm_msm_gpu` trace events in tracefs confirm this file is doing its job.
