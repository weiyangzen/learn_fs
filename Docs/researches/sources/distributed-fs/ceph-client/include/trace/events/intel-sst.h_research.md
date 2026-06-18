# sources/distributed-fs/ceph-client/include/trace/events/intel-sst.h

Purpose: Intel SST audio DSP IPC tracing for message headers, mailbox transfers, and mailbox metadata.

Important APIs/types/functions: Declares trace-event macros/classes `class:sst_ipc_mailbox`, `class:sst_ipc_mailbox_info`, `class:sst_ipc_msg`, `event:sst_ipc_inbox_rdata`, `event:sst_ipc_inbox_read`, `event:sst_ipc_inbox_wdata`, `event:sst_ipc_inbox_write`, `event:sst_ipc_msg_rx`, `event:sst_ipc_msg_tx`, `event:sst_ipc_outbox_rdata`, `event:sst_ipc_outbox_read`, `event:sst_ipc_outbox_wdata`, `event:sst_ipc_outbox_write`. Defines or exports symbolic enums/helpers none. Representative payload fields include `offset:unsigned int`, `size:unsigned int`, `val:unsigned int`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Event classes track IPC messages, mailbox payload buffers, and mailbox info for send/receive/irq/work paths with timestamps and sizes. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: DSP firmware/driver owns persistent mailbox state; trace buffers store headers, pointer addresses, mailbox bytes, and ktime samples. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/types.h>`, `#include <linux/ktime.h>`, `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Mailbox payload capture can be verbose and must respect buffer sizes; firmware ABI changes can make message decode stale. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Exercise SST IPC send/response, IRQ receive, and mailbox dump paths while checking sizes and timing. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/intel-sst`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
