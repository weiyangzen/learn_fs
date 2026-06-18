<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace.c

## Purpose

`xe_trace.c` instantiates Xe tracepoints by defining `CREATE_TRACE_POINTS` before including `xe_trace.h`.

## Important APIs, Types, and Functions

The file has no runtime functions of its own. Its key behavior is conditional inclusion outside sparse checker builds so tracepoint definitions are emitted in exactly one translation unit.

## Control Flow

During compilation, this translation unit expands tracepoint declarations from `xe_trace.h` into definitions. Other files include `xe_trace.h` only as declarations and call trace helpers such as TLB invalidation fence send/receive/signal tracepoints.

## State and Persistence Behavior

Tracepoint registration state is owned by the kernel tracing infrastructure. This file does not maintain driver state.

## Dependencies and Integration Points

It depends on `xe_trace.h` and integrates with all Xe code that emits tracepoints, including TLB invalidation and related GPU/VM paths.

## Risks and Test Signals

If this file is omitted from the build or another file also defines `CREATE_TRACE_POINTS`, tracepoints will fail to link or duplicate. Build tests and tracing smoke tests should verify Xe tracepoints are present and callable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace.c -->
