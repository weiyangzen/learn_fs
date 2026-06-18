# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_trace.c

Purpose: instantiates Lima tracepoints declared in `lima_trace.h`.

Important APIs/types/functions: defines `CREATE_TRACE_POINTS` and includes `lima_trace.h` after including `lima_sched.h`, causing the kernel trace infrastructure to emit storage and metadata for the trace events.

Control flow: no runtime control flow beyond compile-time tracepoint generation. Scheduler code calls `trace_lima_task_submit` and `trace_lima_task_run` when tracepoints are enabled.

State and persistence: tracepoint state is maintained by the kernel tracing subsystem, not this file. It persists only as runtime trace buffers when tracing is active.

Dependencies and integration points: depends on `lima_sched.h` for `struct lima_sched_task` visibility and on Linux tracepoint generation through `trace/define_trace.h` in the header.

Risks and test signals: include ordering and `TRACE_INCLUDE_PATH` must remain correct or build breaks. Test by building the driver with tracepoints enabled and verifying `lima:lima_task_submit` and `lima:lima_task_run` appear under tracing.
