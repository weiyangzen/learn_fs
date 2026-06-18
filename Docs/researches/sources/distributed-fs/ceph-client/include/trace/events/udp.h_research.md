# sources/distributed-fs/ceph-client/include/trace/events/udp.h

Purpose: Defines UDP receive-queue failure tracing for packets that cannot be queued to a socket.

Important APIs/types/functions: `udp_fail_queue_rcv_skb` captures socket identity, network tuple data through `net_probe_common`, skb length, and failure return code.

Control flow: UDP receive paths call the generated helper when `skb` queueing fails. The trace assignment records socket/packet metadata and the error reason.

State/persistence: No socket or skb state is mutated here; only a trace record is persisted.

Dependencies/integration: Includes UDP, tracepoint, and network probe common helpers; consumed by networking diagnostics and perf/ftrace.

Risks: Receive error paths may run under pressure; tracepoint dereferences must be safe for partially processed skbs and sockets.

Test signals: Generate UDP receive buffer pressure while `udp:*` is enabled and confirm failure codes match drop behavior.
