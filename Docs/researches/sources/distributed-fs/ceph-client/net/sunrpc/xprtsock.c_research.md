# sources/distributed-fs/ceph-client/net/sunrpc/xprtsock.c

## Purpose
This file implements the client-side SUNRPC socket transports for AF_LOCAL, UDP, TCP, TCP-with-TLS, and TCP backchannel operation. It adapts Linux sockets to the generic `rpc_xprt` API used by NFS and other RPC clients.

## Important APIs, Types, And Functions
The file defines tunables for slot tables, reserved port ranges, and TCP FIN timeout, plus transport classes `xs_local_transport`, `xs_udp_transport`, `xs_tcp_transport`, `xs_tcp_tls_transport`, and `xs_bc_tcp_transport`. Major functions include address formatting/freeing, XDR receive helpers, stream record parsing, UDP skb receive handling, send paths `xs_local_send_request()`, `xs_udp_send_request()`, `xs_tcp_send_request()`, socket callback installation/restoration, connect workers for local/UDP/TCP/TLS, backchannel allocation/send helpers, setup functions, `init_socket_xprt()`, and `cleanup_socket_xprt()`.

## Control Flow
Transport setup allocates `struct sock_xprt` via `xprt_alloc()`, stores source/destination addresses, initializes workers, selects ops, and registers with SUNRPC transport classes. Connect requests are serialized by `xprt_lock_connect()` and scheduled on `xprtiod_workqueue`. UDP creates and marks the socket connected synchronously in a worker. TCP creates or reuses a socket, binds a reserved source port when required, installs callbacks, starts nonblocking connect, and reacts to socket state changes. TLS creates a lower RPC client, sends an RPC_AUTH_TLS probe, waits for a kernel TLS handshake, then transfers the connected socket to the upper transport. Receive callbacks queue workers that parse UDP datagrams or TCP record fragments, find matching requests by XID, copy into XDR buffers, update RTT/congestion, and complete RPC tasks.

## State And Persistence
State is volatile and per transport: socket/file/sk pointers, source port reuse state, receive and transmit offsets, work items, socket state bits, saved callbacks, TLS handshake completion, and RPC statistics. Sysctl and module parameters persist only while the module/kernel instance is running. Socket callbacks use `sk_user_data` to recover the owning transport.

## Dependencies And Integration Points
Dependencies include Linux socket, UDP/TCP, kernel TLS handshake APIs, SUNRPC scheduler/client/rpcbind/backchannel APIs, XDR buffer helpers, sysctl, tracepoints, workqueues, and optional swap memalloc handling. The file is the socket transport registration point for SUNRPC.

## Risks And Test Signals
Risks include races between callbacks and teardown, partial TCP record sends, reconnect backoff behavior, reserved port exhaustion, TLS alert/error handling, sparse page allocation failures, and preserving old socket callbacks. Build tests should cover all transport configs, including TLS and backchannel. Runtime signals include NFS over TCP/UDP/local socket mounts, RPC-with-TLS success and failure cases, reconnect after server close, bad XID accounting, congestion behavior under UDP loss, reserved-port reuse, and clean module unload unregistering sysctls and transports.
