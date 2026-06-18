# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_uncore_trace.c

Purpose: Instantiates the uncore MMIO tracepoints declared in `intel_uncore_trace.h`.

Important APIs/functions: Defines `CREATE_TRACE_POINTS` before including the trace header, guarded out for `__CHECKER__`.

Control flow: No runtime control flow beyond tracepoint definition emission at compile time.

State/persistence: No state. It creates tracepoint metadata and hooks for the kernel tracing subsystem.

Dependencies/integration: Depends directly on `intel_uncore_trace.h`; MMIO read/write wrappers in `intel_uncore.c` call `trace_i915_reg_rw()`.

Risks: Incorrect include guards or trace include path would break tracepoint generation. The checker guard avoids sparse issues.

Test signals: Build success and availability of `i915_reg_rw` trace events; runtime tracing verifies MMIO access logging.
