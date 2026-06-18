# sources/distributed-fs/ceph-client/include/trace/events/memcg.h

Purpose: Memory cgroup rstat tracepoints for stats/events flushing and flush summary.

Important APIs/types/functions: Declares trace-event macros/classes `class:memcg_rstat_events`, `class:memcg_rstat_stats`, `event:count_memcg_events`, `event:mod_memcg_lruvec_state`, `event:mod_memcg_state`, `trace:memcg_flush_stats`. Defines or exports symbolic enums/helpers none. Representative payload fields include `force:bool`, `id:u64`, `item:int`, `needs_flush:bool`, `stats_updates:s64`, `val:long`, `val:unsigned long`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Event classes record memcg id/path, stat/event names, values, CPU, and flush details as rstat updates propagate. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: memcg/rstat state persists in cgroup structures; trace entries snapshot propagation and flush data. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/memcontrol.h>`, `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Path resolution and high-frequency stat updates can add overhead; stale cgroup names after deletion can complicate analysis. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run memory pressure across cgroups, trigger rstat flushes, and validate stats/events values against cgroupfs. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/memcg`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
