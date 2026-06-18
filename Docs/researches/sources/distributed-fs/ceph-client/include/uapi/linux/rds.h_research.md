<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rds.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rds.h

Purpose: defines the Reliable Datagram Sockets userspace ABI for socket options, control messages, RDMA/atomic operations, zcopy completion, statistics, IPv4/IPv6 info structs, and receive-path latency tracing.

Important APIs and types: socket options include memory registration/freeing, receive errors, congestion monitoring, transport selection, and latency tracing. Control messages include RDMA args/dest/map/status, congestion updates, atomic fetch-add/compare-swap and masked variants, RX latency trace, zcopy cookie/completion. Info structs report counters, connections, messages, sockets, TCP sockets, IB/RDMA connections, and IPv6 variants. RDMA structs describe memory vectors, keys, flags, atomics, notifiers, and status.

Control flow: applications use `SOL_RDS` sockets, set options, send messages with cmsgs for RDMA/atomic/zcopy behavior, receive completions/errors/counters, and query diagnostic info. Kernel RDS transports over TCP/IB route datagrams, manage memory registrations, and update congestion/latency state.

State and persistence: state is runtime per socket, connection, transport, memory registration, congestion map, and message queue. No durable state is defined; RDMA keys and zcopy cookies are lifetime-bound.

Dependencies and integration points: depends on Linux socket, IPv6, and fixed types. Integrates with RDS core, TCP and InfiniBand transports, RDMA memory registration, Oracle/cluster applications, socket diagnostics, and poll/error queues.

Risks and test signals: risks include packed struct compatibility, RDMA key lifetime leaks, cmsg validation, IPv4/IPv6 divergence, atomic operation alignment, congestion wakeups, and zcopy completion loss. Test RDS TCP/IB send/recv, RDMA map/free/status, atomics, congestion monitor polling, recv error queue, IPv6 info queries, and malformed cmsgs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rds.h -->
