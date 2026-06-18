# sources/distributed-fs/ceph-client/drivers/misc/ocxl/trace.c

Purpose: instantiates the OCXL tracepoints declared in `trace.h`.

Important APIs and functions: defines `CREATE_TRACE_POINTS` and includes `trace.h`; no runtime functions are declared here.

Control flow: compile-time tracepoint generation occurs through the Linux tracepoint infrastructure. Runtime behavior is driven by tracepoint call sites in other OCXL files.

State and persistence: no direct state. Generated tracepoint descriptors integrate with ftrace/perf infrastructure.

Dependencies and integration points: must be built exactly once in the OCXL module to materialize trace events. Depends on `trace.h` and `<trace/define_trace.h>` included from that header.

Risks and test signals: duplicate or missing inclusion can cause link errors or missing events. Build tests with tracepoints enabled and runtime tests under `/sys/kernel/tracing/events/ocxl/` should confirm all events appear.
