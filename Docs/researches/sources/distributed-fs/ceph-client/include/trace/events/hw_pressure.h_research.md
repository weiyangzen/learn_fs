# sources/distributed-fs/ceph-client/include/trace/events/hw_pressure.h

Purpose: Hardware pressure tracing for CPU scheduler thermal/pressure updates.

Important APIs/types/functions: Declares trace-event macros/classes `trace:hw_pressure_update`. Defines or exports symbolic enums/helpers none. Representative payload fields include `cpu:int`, `hw_pressure:unsigned long`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. A compact event records CPU id, new hardware pressure value, and whether the update is capped as scheduler topology updates capacity pressure. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: The scheduler owns persistent capacity state; tracing captures point-in-time pressure updates. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Bad CPU ids or pressure scaling in traces can lead to incorrect scheduler performance diagnosis. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Drive thermal/capacity pressure updates and verify trace values match scheduler debugfs or capacity instrumentation. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/hw_pressure`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
