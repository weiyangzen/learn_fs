# sources/distributed-fs/ceph-client/include/trace/events/ksm.h

Purpose: Kernel Samepage Merging tracepoints for scans, enter/exit, merge/remove events, and advisor decisions.

Important APIs/types/functions: Declares trace-event macros/classes `class:ksm_enter_exit_template`, `class:ksm_scan_template`, `event:ksm_enter`, `event:ksm_exit`, `event:ksm_start_scan`, `event:ksm_stop_scan`, `trace:ksm_advisor`, `trace:ksm_merge_one_page`, `trace:ksm_merge_with_ksm_page`, `trace:ksm_remove_ksm_page`, `trace:ksm_remove_rmap_item`. Defines or exports symbolic enums/helpers none. Representative payload fields include `cpu_percent:unsigned int`, `err:int`, `ksm_page:void *`, `mm:void *`, `pages_to_scan:unsigned long`, `pfn:unsigned long`, `rmap_entries:u32`, `rmap_item:void *`, `scan_time:s64`, `seq:int`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events cover scan start/stop, mm enter/exit, merging with KSM pages, removing rmap/items, and advisor output such as scan time/pages/advice. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: KSM tree/rmap/mm state persists in mm/ksm internals; traces snapshot mm pointers, pfn/pages, stable/unstable counts, and advisor metrics. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: KSM traces include process memory pointers and can race with mm teardown; advisor fields need consistent units. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Enable KSM, merge identical pages, unmerge/remove mappings, and run advisor mode while verifying scan and merge counters. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/ksm`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
