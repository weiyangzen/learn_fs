# sources/distributed-fs/ceph-client/include/trace/events/host1x.h

Purpose: NVIDIA Tegra host1x tracepoints for CDMA push buffers, channel submission, syncpoint waits, and wait-check timing.

Important APIs/types/functions: Declares trace-event macros/classes `class:host1x`, `event:host1x_cdma_begin`, `event:host1x_cdma_end`, `event:host1x_channel_open`, `event:host1x_channel_release`, `trace:host1x_cdma_push`, `trace:host1x_cdma_push_gather`, `trace:host1x_cdma_push_wide`, `trace:host1x_channel_submit`, `trace:host1x_channel_submit_complete`, `trace:host1x_channel_submitted`, `trace:host1x_syncpt_load_min`, `trace:host1x_syncpt_wait_check`, `trace:host1x_wait_cdma`. Defines or exports symbolic enums/helpers none. Representative payload fields include `bo:struct host1x_bo *`, `cmdbuf:bool`, `cmdbuf:u32`, `cmdbufs:u32`, `count:int`, `eventid:u32`, `id:u32`, `min:u32`, `name:const char *`, `offset:u32`, `op1:u32`, `op2:u32`, `op3:u32`, `op4:u32`, `relocs:u32`, `syncpt_base:u32`, `syncpt_id:u32`, `syncpt_incrs:u32`, `syncpt_max:u32`, `thresh:u32`, `val:u32`, `words:u32`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Submission paths emit CDMA pushes/gathers, channel submit/submitted/complete, CDMA waits, syncpoint min loads, and syncpoint wait checks with timestamps. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Trace records snapshot channel ids, job ids, syncpoint ids/thresholds, gather offsets/words, and ktime values; host1x hardware and jobs hold real state. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/ktime.h>`, `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Wrong syncpoint or timestamp capture makes GPU job scheduling bugs difficult to correlate with fence completion. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Submit host1x jobs with gathers and syncpoint waits, then verify push order, thresholds, and completion timestamps. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/host1x`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
