# sources/distributed-fs/ceph-client/net/sunrpc/rpcb_clnt.c

## Purpose
`rpcb_clnt.c` is the in-kernel rpcbind client. It creates per-net local rpcbind clients, registers and unregisters server program/version/transport tuples, and performs asynchronous remote port discovery for RPC clients that need autobinding.

## Important APIs, Types, And Functions
Important APIs include `rpcb_create_local()`, `rpcb_put_local()`, `rpcb_register()`, `rpcb_v4_register()`, and `rpcb_getport_async()`. Internal helpers create AF_LOCAL abstract/pathname or loopback TCP clients, build version-specific rpcbind clients, run synchronous SET/UNSET calls, select rpcbind protocol versions, and encode/decode rpcbind v2/v3/v4 XDR procedures. `struct rpcbind_args`, `struct rpcb_info`, `rpcb_procedures2/3/4`, and `rpcb_program` are the central data definitions.

## Control Flow
Local setup first tries `/run/rpcbind.sock` abstract AF_LOCAL, then `/var/run/rpcbind.sock`, then TCP loopback on port 111. A users count protects shared per-net local clients and `rpcb_put_local()` shuts them down when the last user exits. Server registration builds a mapping and calls either rpcbind v2 SET/UNSET or v4 SET/UNSET with universal addresses and netids. Client autobind puts the original task on the transport binding waitqueue, claims the transport binding bit, creates a temporary rpcbind client to the peer's rpcbind service, starts an async child task, and wakes all binding waiters when the child completes.

## State And Persistence
Per-net state in `sunrpc_net` stores `rpcb_local_clnt`, optional v4 `rpcb_local_clnt4`, `rpcb_users`, `rpcb_is_af_local`, and `rpcb_clnt_lock`. Remote autobind state lives briefly in `rpcbind_args`, the transport's `binding` waitqueue, `bind_index`, bound flag, and transport destination port. Procedure stats are stored in version count arrays and `rpcb_stats`.

## Dependencies And Integration Points
This file depends on the generic RPC client/task scheduler, xprtsock transports, `rpc_sockaddr2uaddr()` and `rpc_uaddr2sockaddr()`, tracepoints, credentials, and network namespace storage. It is called by server registration code in `svc.c` and by client transport connection code when an RPC service port is unknown.

## Risks And Edge Cases
Autobind concurrency is delicate: only one task should query rpcbind for a transport while others sleep on `xprt->binding`. Failed v4/v3 lookups advance `bind_index` to fall back, while IPv6 never uses v2. AF_LOCAL local rpcbind clients disable idle timeout because reconnect would require mount namespace context. Registration over v4 may be unavailable, requiring v2 fallback for IPv4 but not IPv6 service registration. XDR string lengths are bounded and overlong strings are truncated with a warning.

## Test Signals
High-value tests include local rpcbind startup fallback across abstract socket, pathname socket, and loopback TCP; v2 and v4 service registration/unregistration; IPv4 and IPv6 `GETPORT`/`GETADDR` lookup; concurrent autobind waiters; rpcbind unavailable or protocol-not-supported fallback; universal address parse failures; and trace/stat counters for rpcbind procedures.
