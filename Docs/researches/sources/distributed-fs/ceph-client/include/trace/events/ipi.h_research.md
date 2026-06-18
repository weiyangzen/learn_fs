# sources/distributed-fs/ceph-client/include/trace/events/ipi.h

Purpose: Inter-processor interrupt tracing for send targets, raises, and handler entry/exit.

Important APIs/types/functions: Declares trace-event macros/classes `class:ipi_handler`, `event:ipi_entry`, `event:ipi_exit`, `trace:ipi_raise`, `trace:ipi_send_cpu`, `trace:ipi_send_cpumask`. Defines or exports symbolic enums/helpers none. Representative payload fields include `callback:void *`, `callsite:void *`, `cpu:unsigned int`, `reason:const char *`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events record target CPU or cpumask and callback names/reasons; handler classes bracket IPI handling. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: IPI delivery state is architecture/scheduler state; trace records sample requested targets and handler activity. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Callback string lifetime and cpumask formatting must remain valid; high-frequency IPIs can produce large traces. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Trigger reschedule, function-call, and custom IPIs and compare send/raise/handler ordering across CPUs. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/ipi`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
