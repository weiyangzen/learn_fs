# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_trace.h

Purpose: declares Lima scheduler trace events for task submission and task execution.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(lima_task)` captures finished fence context, seqno, and scheduler pipe name from `struct lima_sched_task`. `DEFINE_EVENT` creates `lima_task_submit` and `lima_task_run`.

Control flow: event call sites in `lima_sched.c` pass a task pointer. The fast assignment reads `task->base.s_fence->finished` metadata and scheduler name, then `TP_printk` formats the trace line.

State and persistence: trace events record transient task scheduling metadata into ftrace/perf buffers when enabled. No Lima-owned persistent state is modified.

Dependencies and integration points: uses Linux tracepoint macros and requires `TRACE_INCLUDE_PATH ../../drivers/gpu/drm/lima` so generated trace code can locate the header from build output.

Risks and test signals: dereferencing scheduler/fence fields assumes task init/arm completed before trace calls. Test with ftrace enabled during command submission and confirm both submit and run events carry coherent context/seqno/pipe values.
