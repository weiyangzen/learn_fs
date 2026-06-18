# sources/distributed-fs/ceph-client/include/trace/events/iscsi.h

Purpose: iSCSI transport/session logging tracepoints using shared formatted-message classes.

Important APIs/types/functions: Declares trace-event macros/classes `class:iscsi_log_msg`, `event:iscsi_dbg_conn`, `event:iscsi_dbg_eh`, `event:iscsi_dbg_session`, `event:iscsi_dbg_sw_tcp`, `event:iscsi_dbg_tcp`, `event:iscsi_dbg_trans_conn`, `event:iscsi_dbg_trans_session`. Defines or exports symbolic enums/helpers none. Representative payload fields include `dname`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events mirror iSCSI debug categories such as session, connection, endpoint, TCP, error, and login logging with dynamically formatted messages. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Trace buffers hold formatted strings; iSCSI session/connection state remains in transport structures. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Formatted logging must avoid unbounded strings and may expose target/session identifiers. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Exercise login, connection recovery, command errors, endpoint teardown, and TCP transport logs with tracing enabled. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/iscsi`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
