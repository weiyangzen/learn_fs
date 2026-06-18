# sources/distributed-fs/ceph-client/net/tipc/trace.c

## Purpose
Provides concrete tracepoint support helpers for TIPC. It defines tracepoints by including `trace.h` under `CREATE_TRACE_POINTS`, owns the socket trace filter sysctl storage, and formats skbs and skb queues into compact trace buffers.

## Important APIs, Types, And Functions
`sysctl_tipc_sk_filter[5]` stores `(portid, sock type, name type, lower, upper)` filtering data consumed by `tipc_sk_filtering` in `socket.c`. `tipc_skb_dump` formats TIPC message header fields, user/type/size/node/seq/ack data, protocol-specific fields, optional skb metadata, and TIPC skb control block fields. `tipc_list_dump` summarizes skb queues, either head/tail or first/last five entries.

## Control Flow And State
Trace helper calls are synchronous from tracepoint fast-assign paths. They write into tracepoint-provided dynamic arrays sized by constants from `trace.h`, use `scnprintf` to avoid overflow, and avoid mutating packets. The only persistent state is the socket filter array, which sysctl updates can change at runtime.

## Dependencies And Integration Points
Depends on TIPC message accessors, skb control block layout, Linux tracepoint generation, and the sysctl table in `sysctl.c`. `trace.h` trace events call these helpers for socket, link, node, list, and skb dumps.

## Risks And Test Signals
Risk comes from formatting assumptions changing with message layout, trace buffer truncation hiding important fields, and trace helpers being called from sensitive paths. Test signals include enabling TIPC tracepoints via ftrace/perf, dumping null and non-null skbs/queues, verifying sysctl filter effects, and exercising link, socket, multicast, and overload paths while tracing is active.
