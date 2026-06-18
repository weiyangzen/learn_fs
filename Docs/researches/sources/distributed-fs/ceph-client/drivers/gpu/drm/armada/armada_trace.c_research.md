## sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_trace.c

Purpose: tracepoint definition translation unit for Armada DRM. It enables exactly one `CREATE_TRACE_POINTS` include of `armada_trace.h` when not being parsed by sparse/checker.

Important API is not a function but the tracepoint instantiation pattern required by Linux tracing. Control flow is compile-time: including this file creates the trace event descriptors for events declared in the header.

State is kernel tracing metadata and runtime trace buffers managed by ftrace/perf, not driver-owned persistent state. Dependencies are `armada_trace.h` and Linux trace infrastructure. Risks are duplicate tracepoint definition if `CREATE_TRACE_POINTS` is defined elsewhere, or missing tracepoints if this object is not linked. Test signals are successful build, tracefs events under the `armada` system, and visible records when IRQ or overlay update paths fire.
