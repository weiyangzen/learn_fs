# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/transport.c

## Purpose
`transport.c` is the client-side SunRPC transport switch implementation for RPC/RDMA. It registers the `rdma`/`rdma6` transport class, allocates and destroys `struct rpcrdma_xprt`, formats transport addresses, drives connection attempts through background work, implements request slot and buffer allocation, handles send requests, exposes stats, and registers debug sysctls.

## Important APIs, types, and functions
The main integration object is `xprt_rdma_procs`, a `struct rpc_xprt_ops` table. `xprt_setup_rdma()` allocates the RPC transport and RDMA request buffer pool. `xprt_rdma_connect_worker()` calls `rpcrdma_xprt_connect()` and wakes pending RPC tasks. `xprt_rdma_connect()`, `xprt_rdma_close()`, `xprt_rdma_timer()`, and `xprt_rdma_set_connect_timeout()` implement connection policy. `xprt_rdma_alloc_slot()` and `xprt_rdma_free_slot()` integrate `rpcrdma_buffer_get/put()` with SunRPC slot scheduling. `xprt_rdma_send_request()` marshals and posts one request. `xprt_rdma_init()` and `xprt_rdma_cleanup()` register/unregister transport classes.

## Control flow
Mount or client creation calls `xprt_setup_rdma()`, which takes a module reference, allocates `rpc_xprt` plus embedded RDMA transport, sets timeouts and ops, copies the server address, formats display strings, creates the buffer pool, and initializes delayed connect work. When SunRPC wants a connection, `xprt_rdma_connect()` schedules `xprt_rdma_connect_worker()`, optionally after reconnect backoff. The worker creates RDMA endpoint resources, sets connected state on success, or disconnects and wakes tasks with an error. For each RPC, SunRPC allocates an RDMA slot, allocates or resizes registered send/receive buffers, and invokes `xprt_rdma_send_request()`, which checks connection state and congestion, calls `rpcrdma_marshal_req()`, posts via `frwr_send()`, and drops the connection for stale cookies or no-reply RPCs to keep credit accounting sound.

## State and persistence behavior
State is in `rpc_xprt` and embedded `rpcrdma_xprt`: address strings, timeout values, connect worker, request buffer pool, congestion window, stats, and endpoint pointer. Debug sysctl tunables are global while registered. No disk persistence is used. Address strings allocated during setup are freed during destroy or failed setup. The module reference held by setup is released in destroy.

## Dependencies and integration points
This file depends on the SunRPC transport framework, rpcbind, module/sysctl APIs, `verbs.c` for connect/disconnect and buffer management, `rpc_rdma.c` for marshaling and stats, FRWR posting, and optional backchannel hooks. It exports address formatting and stats helpers used by backchannel server code.

## Risks and edge cases
Request slot allocation has a backlog race that is handled by a recheck after sleeping. `xprt_rdma_send_request()` suppresses retransmit when connect cookies indicate stale sends and closes connections for no-reply RPCs to reset credits. Buffer allocation must resize registered buffers without leaking existing DMA mappings. Connection worker PF_MEMALLOC handling matters for swapper transports. Sysctl registration is debug-conditional and cleanup must unregister both forward and backchannel transports.

## Test signals
Tests should cover transport setup failure unwind, address formatting for IPv4/IPv6, rpcbind port update, connect success/failure/backoff, timeout-triggered disconnect, slot exhaustion and backlog wakeup, buffer resize failure, stale connect-cookie send, no-reply RPC disconnect, stats formatting, sysctl registration, and module cleanup. Useful signals are `xprt_rdma_print_stats()`, tracepoints for connect/send/timeout/disconnect, SunRPC task wake statuses, and request buffer pool counts.
