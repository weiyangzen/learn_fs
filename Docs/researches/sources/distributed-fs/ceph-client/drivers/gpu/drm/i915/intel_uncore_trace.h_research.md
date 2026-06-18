# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_uncore_trace.h

Purpose: Declares the `i915_reg_rw` trace event used for i915 MMIO reads and writes.

Important APIs/types: `TRACE_EVENT_CONDITION(i915_reg_rw, ...)` records write/read flag, register offset, value, access length, and a caller-provided `trace` condition. Trace include path/file metadata points back to the i915 trace header location.

Control flow: The trace event only emits when `trace` is true. Fast assignment converts `i915_reg_t` to offset and stores a 64-bit value so 8/16/32/64-bit reads can share the same event.

State/persistence: No driver state; trace records are transient in ftrace/perf buffers.

Dependencies/integration: Includes `i915_reg_defs.h`, Linux tracepoint headers, and is included by `intel_uncore.c` accessors and `intel_uncore_trace.c` for instantiation.

Risks: Tracepoints can expose high-volume MMIO traffic and should remain conditionally controlled. Format assumes values can be represented as two 32-bit halves.

Test signals: Enabled kernel tracing should show formatted `read/write reg=..., len=..., val=...` events for traced uncore accessors.
