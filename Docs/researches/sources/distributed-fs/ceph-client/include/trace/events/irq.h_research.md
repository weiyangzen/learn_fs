# sources/distributed-fs/ceph-client/include/trace/events/irq.h

Purpose: IRQ, softirq, and tasklet tracepoints for hard IRQ handler entry/exit and bottom-half lifecycle.

Important APIs/types/functions: Declares trace-event macros/classes `class:softirq`, `class:tasklet`, `event:softirq_entry`, `event:softirq_exit`, `event:softirq_raise`, `event:tasklet_entry`, `event:tasklet_exit`, `trace:irq_handler_entry`, `trace:irq_handler_exit`. Defines or exports symbolic enums/helpers `sirq##_SOFTIRQ`. Representative payload fields include `func:void *`, `irq:int`, `name`, `ret:int`, `tasklet:void *`, `vec:unsigned int`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Hard IRQ events record irq number, action name, and return; softirq and tasklet classes record vector/action and handler function addresses for raise/entry/exit. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Interrupt controller and softirq subsystem own state; tracing records execution samples. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: High-rate IRQ tracing can perturb latency, and enum/vector names must stay synchronized with softirq definitions. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Generate hard IRQs, softirqs, and tasklets while validating entry/exit pairs and handler names. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/irq`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
