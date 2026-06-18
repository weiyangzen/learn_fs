# sources/distributed-fs/ceph-client/net/sunrpc/svc_xprt.c

## Purpose
`svc_xprt.c` implements server-side SUNRPC transport class registration, listener creation, transport scheduling, request receive/send coordination, temporary connection aging, shutdown, deferred request replay, listener lookup, and pool statistics.

## Important APIs, Types, And Functions
Important APIs include `svc_reg_xprt_class()`, `svc_unreg_xprt_class()`, `svc_print_xprts()`, `svc_xprt_deferred_close()`, `svc_xprt_put()`, `svc_xprt_init()`, `svc_xprt_received()`, `svc_xprt_create_from_sa()`, `svc_xprt_create()`, `svc_xprt_copy_addrs()`, `svc_print_addr()`, `svc_xprt_enqueue()`, `svc_reserve()`, `svc_wake_up()`, `svc_recv()`, `svc_send()`, `svc_age_temp_xprts_now()`, `svc_xprt_close()`, `svc_xprt_destroy_all()`, `svc_find_listener()`, `svc_find_xprt()`, `svc_xprt_names()`, and `svc_pool_stats_open()`.

## Control Flow
Transport classes register globally by name. Creating a listener finds the class, module-gets it, calls the provider's create op, attaches credentials, adds a permanent xprt, and enqueues it. Providers set `XPT_CONN`, `XPT_DATA`, `XPT_CLOSE`, `XPT_HANDSHAKE`, or `XPT_DEFERRED` and call `svc_xprt_enqueue()`. Service threads call `svc_recv()`, allocate argument pages, wait as idle workers, dequeue a busy xprt, and `svc_handle_xprt()` accepts new connections, performs TLS handshakes, receives deferred or fresh requests, reserves reply space, calls `svc_process()`, and releases the transport. Replies go through provider `xpo_sendto()`.

## State And Persistence
Global state is the registered transport class list and `svc_rpc_per_connection_limit` module parameter. Each `svc_xprt` tracks class/ops, refcount, flags, server, net namespace, credentials, local/remote addresses, ready-queue node, reserved reply bytes, active request count, deferred requests, users, auth cache, and optional backchannel xprt/switch. Service state tracks permanent and temporary lists, temporary connection count, aging timer, and per-pool ready queues/counters.

## Dependencies And Integration Points
The file depends on transport providers such as TCP/UDP svc sockets, service pools from `svc.c`, rpcbind unregister through `svc_register()`, auth cache release from `svcauth_unix.c`, cache deferral infrastructure, XDR buffers, socket address helpers, module loading via `request_module("svc%s")`, tracepoints, and optional backchannel transports.

## Risks And Edge Cases
`XPT_BUSY` is the key serialization bit; clearing it can allow another thread to close and put the transport, so references must be held around re-enqueue. Slot limiting and reserved bytes use memory barriers with readiness checks to avoid stalls. Temporary unauthenticated connections are hard-limited and aged with mark-and-sweep. Deferred requests only handle small non-paged buffers. Shutdown must close xprts even if no service threads are running, while avoiding deletion of transports owned by another net namespace.

## Test Signals
High-value tests include transport class duplicate registration, autoload of svc transport modules, listener create for IPv4/IPv6 and unsupported families, accept/data/handshake/close scheduling, per-connection RPC limit, reply reservation accounting, temp connection aging and address removal notifier path, deferred cache miss replay/drop, service shutdown with and without worker threads, listener lookup/names output, and pool stats seq output.
