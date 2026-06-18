# sources/distributed-fs/ceph-client/include/trace/events/mctp.h

Purpose: MCTP key lifecycle tracing for key acquisition and release reasons.

Important APIs/types/functions: Declares trace-event macros/classes `trace:mctp_key_acquire`, `trace:mctp_key_release`. Defines or exports symbolic enums/helpers `MCTP_TRACE_KEY_CLOSED`, `MCTP_TRACE_KEY_DROPPED`, `MCTP_TRACE_KEY_INVALIDATED`, `MCTP_TRACE_KEY_REPLIED`, `MCTP_TRACE_KEY_TIMEOUT`. Representative payload fields include `laddr:__u8`, `paddr:__u8`, `reason:int`, `tag:__u8`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events record key pointer, local/peer endpoint ids, tag, owner, and symbolic release reasons such as timeout, replied, invalidated, closed, or dropped. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: MCTP routing/key state persists in the network subsystem; trace entries snapshot key lifecycle metadata. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Key pointer reuse and endpoint/tag wraparound can confuse correlation in long traces. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run MCTP request/reply, timeout, socket close, invalidation, and drop cases while checking acquire/release matching. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/mctp`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
