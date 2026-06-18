# sources/distributed-fs/ceph-client/include/linux/sunrpc/xprt.h

Purpose: declares the SUNRPC client transport layer, request slot structure, transport operations, transport class registration, congestion/window state, connection state bits, and generic transport helpers.

Important APIs and types: `struct rpc_rqst` tracks send/receive XDR buffers, task/cred/XID, GSS sequence history, encryption scratch pages, slot/receive/send queue nodes, call/reply buffers, byte counts, timeout/retry/connect state, partial-send progress, timestamps, pins, and optional backchannel preallocation. `enum xprtsec_policies` and `struct xprtsec_parms` configure none/anonymous TLS/X.509 TLS. `struct rpc_xprt_ops` defines buffer sizing, slot reservation, rpcbind, connect, send, receive wait, timer, close, destroy, swap, disconnect injection, and backchannel hooks. `struct rpc_xprt` owns refcount, ops, address, protocol, congestion/cwnd, wait queues, slot table, state bits, connection timers, locks, XID generator, send/receive queues, stats, net namespace, display strings, debug/sysfs objects, class, and multipath flags.

Control flow: tasks reserve a slot and transport, bind/connect if needed, enqueue transmit/receive, send requests, wait for replies, update RTT/congestion, complete or retransmit, then release slots and transport references. State-bit helpers manage connected, connecting, bound, and binding transitions with memory barriers where needed.

State and persistence: transport state is runtime client/connection state: slots, queues, congestion windows, timers, stats, addresses, reconnect cookies, and optional backchannel pools. It does not persist beyond client/transport lifetime.

Dependencies and integration points: integrates RPC scheduler, XDR, message protocol constants, sockets/RDMA/local transport classes, net namespaces, sysfs/debugfs, TLS policy, NFS backchannel, and multipath.

Risks and test signals: risks include slot leaks, XID lookup races, congestion accounting errors, reconnect cookie misuse, state-bit memory ordering, send/receive queue races, and TLS/backchannel interactions. Test with TCP/UDP/RDMA/local transports, retransmits, disconnect/reconnect, congestion, high slot counts, GSS privacy, and multipath failover.
