# sources/distributed-fs/ceph-client/include/trace/events/iocost.h

Purpose: blk-iocost controller tracing for iocg activation/inactivation, inuse updates, vrate adjustment, and debt forgiveness.

Important APIs/types/functions: Declares trace-event macros/classes `class:iocg_inuse_update`, `class:iocost_iocg_state`, `event:iocost_inuse_adjust`, `event:iocost_inuse_shortage`, `event:iocost_inuse_transfer`, `event:iocost_iocg_activate`, `event:iocost_iocg_idle`, `trace:iocost_ioc_vrate_adj`, `trace:iocost_iocg_forgive_debt`. Defines or exports symbolic enums/helpers none. Representative payload fields include `busy_level:int`, `cgroup`, `cur_period:u64`, `devname`, `hweight_active:u64`, `hweight_inuse:u64`, `inuse:u32`, `last_period:u64`, `new_debt:u64`, `new_delay:u64`, `new_hweight_inuse:u64`, `new_inuse:u32`, `new_vrate:u64`, `now:u64`, `nr_lagging:int`, `nr_shortages:int`, `old_debt:u64`, `old_delay:u64`, `old_hweight_inuse:u64`, `old_inuse:u32`, `old_vrate:u64`, `read_missed_ppm:u32`, `rq_wait_pct:u32`, `usage_pct:u32`, `vnow:u64`, `vrate:u64`, `vtime:u64`, `weight:u32`, ... plus 1 more.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Event classes record cgroup path, device major/minor, active/debt/inuse/weight/hweight/vtime metrics, and controller virtual-rate changes. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: The block cgroup controller owns persistent cost model state; traces sample iocg/ioc fields during recalculation and forgiveness. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Cgroup path resolution and high-resolution virtual time values can be expensive or misleading if sampled after state changes. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run blk-iocost workloads with active/inactive cgroups, weight changes, debt, and vrate adjustment while checking metrics. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/iocost`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
