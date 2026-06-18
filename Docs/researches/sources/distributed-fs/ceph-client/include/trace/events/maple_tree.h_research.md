# sources/distributed-fs/ceph-client/include/trace/events/maple_tree.h

Purpose: Maple tree tracing for operations, reads, and writes over tree nodes/ranges.

Important APIs/types/functions: Declares trace-event macros/classes `trace:ma_op`, `trace:ma_read`, `trace:ma_write`. Defines or exports symbolic enums/helpers none. Representative payload fields include `fn:const char *`, `index:unsigned long`, `last:unsigned long`, `max:unsigned long`, `min:unsigned long`, `node:void *`, `piv:unsigned long`, `val:void *`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events record operation name, tree/node pointers, index/last ranges, slots, and values during maple-tree reads/writes. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Maple tree storage is persistent in caller-owned structures; trace entries are transient snapshots of traversal/update state. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Pointer/range traces are useful but can expose address-space layout; stale node pointers after mutation require careful ordering. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run maple tree insert/find/erase/split tests and verify read/write range and node event consistency. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/maple_tree`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
