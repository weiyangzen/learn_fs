# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma_backchannel.c

## Purpose
`svc_rdma_backchannel.c` implements server-side support for reverse-direction RPCs over RPC/RDMA, used by NFS backchannel callbacks. It creates a lightweight backchannel `rpc_xprt`, sends reverse-direction Calls using server RDMA send contexts, and handles incoming backchannel Replies received by the service receive path.

## Important APIs, types, and functions
`svc_rdma_handle_bc_reply()` matches an incoming RDMA_MSG Reply to a pending backchannel `rpc_rqst`, copies reply data into the request receive buffer, updates backchannel credits, and completes the RPC task. `xprt_rdma_bc_allocate()` and `xprt_rdma_bc_free()` allocate a page-sized send buffer plus receive buffer for reverse Calls. `rpcrdma_bc_send_request()` builds a minimal RPC/RDMA header with no chunks and calls `svc_rdma_bc_sendto()`. `xprt_rdma_bc_send_request()` is the `rpc_xprt_ops.send_request` hook and closes the service xprt on `-ENOTCONN`. `xprt_setup_rdma_bc()` allocates and binds a pre-connected `rpc_xprt` to an existing `svc_xprt`.

## Control flow
Backchannel setup is triggered through the `xprt_class xprt_rdma_bc` setup callback. The new transport is marked bound and connected, inherits destination addressing, installs `xprt_rdma_bc_procs`, stores the service transport in `bc_xprt`, and stores the new client xprt in `xpt_bc_xprt`. To send a callback, SunRPC allocates buffers, marshals the RPC Call into the page, then invokes `xprt_rdma_bc_send_request()`. That obtains a server send context, writes the RPC/RDMA fixed header and absent chunk lists, maps the reply message through `svc_rdma_map_reply_msg()`, and posts an RDMA Send. Incoming Replies are detected in `svc_rdma_recvfrom.c` and passed to `svc_rdma_handle_bc_reply()`.

## State and persistence behavior
Backchannel state is all in memory. The `rpc_xprt` uses congestion-window credits derived from Reply headers, bounded by `rb_bc_max_requests`. The service transport and backchannel transport hold references to each other; the final put is coordinated by server transport free paths. Each reverse Call buffer owns a page and kmalloc receive area for the life of the RPC task.

## Dependencies and integration points
This file bridges SunRPC client backchannel operations with server RPC/RDMA send helpers from `svc_rdma_sendto.c`. It uses `xprt_lookup_rqst()`, request pinning, congestion-window helpers, `svc_rdma_send_ctxt_get/put()`, `svc_rdma_map_reply_msg()`, `svc_rdma_post_send()`, and address formatting from the client transport. It is compiled when SUNRPC backchannel support is enabled and is registered by `transport.c`.

## Risks and edge cases
The backchannel path deliberately does not support chunks, so large callbacks over one page are rejected. `svc_rdma_bc_sendto()` increments the callback buffer page refcount so Send completion cannot release it before retransmits are done. `svc_rdma_handle_bc_reply()` must avoid buffer overflow by comparing destination and source iov lengths. Credit grants of zero are forced to one to prevent deadlock. If no send context is available or posting fails, the service connection is dropped.

## Test signals
Coverage should include backchannel setup/teardown reference counts, reverse Call send success, no-send-context failure, oversized callback buffer rejection, incoming Reply XID mismatch, short destination receive buffer handling, zero and excessive credit grants, and connection close on send errors. Tracepoints from send mapping/posting plus SunRPC backchannel completion are the primary runtime signals.
