
# sources/distributed-fs/ceph-client/include/trace/events/sunrpc.h

## Purpose
Defines the comprehensive SunRPC client/server tracepoint catalog used by NFS, lockd, RPCSEC_GSS, RPC transports, rpcbind, server sockets, service pools, caches, and registration paths.

## Important APIs, Types, and Functions
The header exports symbolic decoders for socket types, address families, xprt security policies, client create flags, auth statuses, task flags/runstate, socket states, transport state, service deferral, cache status, and registration operations. Event classes cover XDR buffers, clients, task status/running/queued states, failures, replies, sockets, xprt lifetimes/events, write-lock/congestion, TLS, service XDR messages/buffers, service requests/status, service transports, pools, deferred requests, svcsock lifetimes/classes, cache events, and register events. Named events span `rpc_xdr_*`, `rpc_clnt_*`, `rpc_request`, `rpc_task_*`, bad call/verifier events, reply/rpcb errors, `rpc_buf_alloc`, `rpc_call_rpcerror`, latency and XDR overflow/alignment events, `rpc_socket_*`, `xprt_*`, rpcbind port/register operations, TLS events, `svc_*`, `svc_xprt_*`, `svcsock_*`, cache events, and `svc_unregister`.

## Control Flow
Client-side RPC code emits events during client creation, task scheduling, queueing, run actions, sleeps/wakes, buffer allocation, XDR encode/decode, socket connect/error/state changes, transport reservation/transmit/retransmit/ping, congestion and writelock changes, rpcbind lookup/set/register/unregister, and TLS handshakes. Server-side code emits events during request receive/decode/authenticate/process/send, XDR buffer handling, transport create/enqueue/dequeue/accept/close, pool-thread lifecycle, deferred request handling, socket receive/accept/state, cache lookup/update, and service registration/unregistration.

## State and Persistence
This header owns no RPC state. Trace records snapshot task ids, client ids, XIDs, program/procedure names, versions, server names, transport ids, addresses, ports, socket states, XDR buffer layout, queue names, timeouts, latencies, errors, request statuses, service pool data, and cache identifiers. Dynamic strings and arrays are copied into trace records to survive object reuse.

## Dependencies and Integration Points
Depends on SunRPC headers (`sched.h`, `clnt.h`, `svc.h`, `xprtsock.h`, `svc_xprt.h`), TCP state definitions, `linux/net.h`, `trace/misc/sunrpc.h`, `trace/events/net_probe_common.h`, and tracepoint infrastructure. Integrates directly with NFS client/server, rpcbind, RPC transports over TCP/UDP/TLS/RDMA-adjacent code, RPCSEC_GSS, kernel service caches, and user diagnostics through tracefs/perf/BPF.

## Risks
This is a large trace ABI surface; field or symbolic-name changes can break NFS/RPC observability tools. Many events are hot under NFS workloads, so enabling broad tracing can be expensive. Events expose server names, addresses, ports, procedure names, XIDs, and sometimes auth/cache outcomes. Call sites must pass initialized RPC objects because event assignments dereference nested pointers.

## Test Signals
Signals include NFS mount/read/write/unmount traces, server-side nfsd request handling, rpcbind success/failure paths, socket connect/reset/no-space tests, TLS-enabled RPC, retransmission and timeout injection, XDR overflow/alignment tests, service cache operations, BPF attachment to representative events, and trace format stability checks.
