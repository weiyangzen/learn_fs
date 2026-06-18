# sources/distributed-fs/ceph-client/include/trace/events/irq_matrix.h

Purpose: IRQ matrix allocator tracing for global and per-CPU vector accounting.

Important APIs/types/functions: Declares trace-event macros/classes `class:irq_matrix_cpu`, `class:irq_matrix_global`, `class:irq_matrix_global_update`, `event:irq_matrix_alloc`, `event:irq_matrix_alloc_managed`, `event:irq_matrix_assign`, `event:irq_matrix_assign_system`, `event:irq_matrix_free`, `event:irq_matrix_offline`, `event:irq_matrix_online`, `event:irq_matrix_remove_managed`, `event:irq_matrix_remove_reserved`, `event:irq_matrix_reserve`, `event:irq_matrix_reserve_managed`. Defines or exports symbolic enums/helpers none. Representative payload fields include `allocated:unsigned int`, `available:unsigned int`, `bit:int`, `cpu:unsigned int`, `global_available:unsigned int`, `global_reserved:unsigned int`, `managed:unsigned int`, `online:bool`, `online_maps:unsigned int`, `total_allocated:unsigned int`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events record matrix online/available/allocated/reserved counts, global updates, and CPU-local vector allocation/free/reservation transitions. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: The irq_matrix object owns persistent vector allocation; trace entries sample counters and CPU id. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Counter snapshots must be taken while allocator state is coherent or CPU hotplug/vector leak debugging becomes unreliable. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Stress IRQ vector allocation/free, CPU hotplug, managed vectors, and reservation paths with tracefs enabled. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/irq_matrix`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
