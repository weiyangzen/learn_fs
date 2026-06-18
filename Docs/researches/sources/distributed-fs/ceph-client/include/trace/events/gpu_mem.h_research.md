# sources/distributed-fs/ceph-client/include/trace/events/gpu_mem.h

Purpose: GPU memory accounting tracepoint for per-process and per-GPU total allocation updates.

Important APIs/types/functions: Declares trace-event macros/classes `trace:gpu_mem_total`. Defines or exports symbolic enums/helpers none. Representative payload fields include `gpu_id:uint32_t`, `pid:uint32_t`, `size:uint64_t`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. A single event records gpu_id, process id, and total size as GPU drivers update memory accounting. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Persistent accounting is maintained by drivers; the trace entry is a sampled total in the tracing ring. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Drivers must agree on gpu_id and size units or cross-driver memory dashboards become inconsistent. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Allocate/free GPU buffers in a driver using this tracepoint and verify totals return to baseline per pid and GPU. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/gpu_mem`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
