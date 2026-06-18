# sources/distributed-fs/ceph-client/drivers/gpu/trace/trace_gpu_mem.c

Purpose: instantiates GPU memory tracepoints.

Important APIs: defines `CREATE_TRACE_POINTS` before including `<trace/events/gpu_mem.h>`, then exports `gpu_mem_total` with `EXPORT_TRACEPOINT_SYMBOL`.

Control flow: no active runtime logic. The tracepoint infrastructure emits events when producers call the generated trace hooks.

State and persistence: no file-local state; tracepoint registration is handled by kernel trace infrastructure.

Dependencies and integration: depends on `linux/module.h` and trace event definitions in `trace/events/gpu_mem.h`. GPU drivers and tracing tools integrate through the exported tracepoint.

Risks: this file only creates the tracepoint symbols; event schema changes happen in the trace header. Consumers depend on stable trace event fields.

Test signals: tracepoint visible in tracing filesystem and successful driver emission of `gpu_mem_total`.
