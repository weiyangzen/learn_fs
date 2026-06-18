# sources/distributed-fs/ceph-client/include/trace/events/handshake.h

Purpose: Network handshake and TLS record tracepoints for kernel TLS handshake request lifecycle, file descriptor handoff, errors, alerts, completion, and content types.

Important APIs/types/functions: Declares trace-event macros/classes `class:handshake_alert_class`, `class:handshake_error_class`, `class:handshake_event_class`, `class:handshake_fd_class`, `event:name`, `trace:handshake_complete`, `trace:tls_contenttype`. Defines or exports symbolic enums/helpers `TLS_ALERT_DESC_##x`, `TLS_ALERT_LEVEL_FATAL`, `TLS_ALERT_LEVEL_WARNING`, `TLS_RECORD_TYPE_##x`. Representative payload fields include `daddr:__u8`, `description:unsigned long`, `err:int`, `fd:int`, `level:unsigned long`, `netns_ino:unsigned int`, `req:const void *`, `saddr:__u8`, `sk:const void *`, `status:int`, `type:unsigned long`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Event classes record request ids, socket addresses, file descriptors, negative errors, TLS alert level/description, session status, peer identity, and content type decode. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: The tracepoint stores no session; it snapshots handshake request/socket/TLS values while the handshake service and TLS stack own state. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/net.h>`, `#include <net/tls_prot.h>`, `#include <linux/tracepoint.h>`, `#include <trace/events/net_probe_common.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Stringified peer names and socket addresses can be privacy-sensitive, and missing enum coverage for TLS alerts/content types reduces diagnosis value. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run successful and failing kTLS handshakes, fd handoff, alert paths, and TLS record receipt while verifying address and enum printing. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/handshake`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
