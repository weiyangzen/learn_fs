# sources/distributed-fs/ceph-client/include/trace/events/initcall.h

Purpose: Kernel initcall tracing for initcall level, start, and finish timing/results.

Important APIs/types/functions: Declares trace-event macros/classes `trace:initcall_finish`, `trace:initcall_level`, `trace:initcall_start`. Defines or exports symbolic enums/helpers none. Representative payload fields include `level`, `ret:int`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Boot-time initcall execution emits level changes, function start pointers, and finish events with return value and duration. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: No persistent state is owned; tracing snapshots boot sequencing and timing metadata. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Function pointer printing depends on kallsyms/symbolization, and long initcall durations need correct units. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Boot with initcall tracing enabled and compare start/finish nesting, levels, return codes, and durations with dmesg initcall debug. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/initcall`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
