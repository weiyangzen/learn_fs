<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_trace.h

## Purpose
Defines Linux tracepoints for i915 GEM object lifecycle, VMA binding, eviction, request lifecycle/waits, optional low-level request and context events, PPGTT lifetime, and GEM context lifetime.

## Important APIs, types, and functions
- Trace events include `i915_gem_object_create`, `i915_gem_shrink`, `i915_vma_bind`, `i915_vma_unbind`, object pwrite/pread/fault, object clflush/destroy, eviction events, `i915_request_queue`, request add/retire/wait begin/end, PPGTT create/release, and context create/free.
- Low-level tracepoints gated by `CONFIG_DRM_I915_LOW_LEVEL_TRACEPOINTS` include request GuC submit/submit/execute/in/out and many Intel context state events.
- When low-level tracing is disabled, inline no-op functions preserve call sites.
- `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` configure trace header generation.

## Control flow
Tracepoint macros describe argument capture and formatted print output. Request tracepoints record device index, engine class/instance, fence context/seqno, tail, flags, priority, port, or completion state. Context tracepoints record GuC ID, pin count, scheduler state, and GuC priority.

## State and persistence
Tracepoints do not store persistent driver state beyond transient ftrace/perf buffers. They observe live GEM, VM, request, and context fields at trace call time.

## Dependencies and integration points
Depends on Linux tracepoint infrastructure, DRM device types, Intel engine helpers, and i915 request/context/GEM structures. Used by request code, GEM memory management, VM code, GuC/execlists backend instrumentation, and debugging tools.

## Risks
Tracepoint field layouts are consumed by tooling, so changing event names or field names can break diagnostics. Capturing pointer fields and racy request completion state is acceptable for tracing but should not be interpreted as synchronization. Low-level no-op stubs must match real tracepoint signatures.

## Test signals
Builds with tracing on/off, `trace-cmd`/ftrace event availability, request lifecycle traces matching add/submit/execute/retire ordering, GEM object/VM leak debugging, and low-level GuC/context trace validation when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_trace.h -->
