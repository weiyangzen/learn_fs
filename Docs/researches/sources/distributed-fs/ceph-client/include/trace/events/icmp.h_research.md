# sources/distributed-fs/ceph-client/include/trace/events/icmp.h

Purpose: ICMP send tracing for generated IPv4 ICMP errors and control messages.

Important APIs/types/functions: Declares trace-event macros/classes `trace:icmp_send`. Defines or exports symbolic enums/helpers none. Representative payload fields include `code:int`, `daddr:__u8`, `dport:__u16`, `saddr:__u8`, `skbaddr:const void *`, `sport:__u16`, `type:int`, `ulen:unsigned short`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. The event records SKB address, source/destination addresses, ICMP type/code, interface index, and original IP header fields when icmp_send is invoked. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Network stack state persists in the skb and routes; trace entries snapshot selected header and device data. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/icmp.h>`, `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Malformed or non-linear skbs can make header extraction delicate, and addresses may be sensitive in production traces. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Trigger TTL exceeded, port unreachable, fragmentation-needed, and filtered cases and verify addresses and ICMP type/code output. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/icmp`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
