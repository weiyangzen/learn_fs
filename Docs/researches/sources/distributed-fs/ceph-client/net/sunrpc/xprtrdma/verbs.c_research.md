# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/verbs.c

## Purpose
`verbs.c` encapsulates client-side RDMA CM and verbs resource management for RPC/RDMA. It creates endpoints, negotiates connections, allocates CQs/QPs/PDs, manages Send and Receive context pools, posts Receive WRs, handles Send and Receive completions, owns request/reply buffer pools, manages memory registration pools, and maps/unmaps registered buffers.

## Important APIs, types, and functions
Endpoint lifecycle is handled by `rpcrdma_ep_create()`, `rpcrdma_xprt_connect()`, `rpcrdma_xprt_disconnect()`, `rpcrdma_xprt_drain()`, and `rpcrdma_ep_destroy()`. RDMA CM events are processed by `rpcrdma_cm_event_handler()`. Completion handlers are `rpcrdma_wc_send()` and `rpcrdma_wc_receive()`. Send context ring operations are `rpcrdma_sendctxs_create()`, `rpcrdma_sendctx_get_locked()`, and `rpcrdma_sendctx_put_locked()`. Buffer APIs include `rpcrdma_buffer_create()`, `rpcrdma_buffer_get()`, `rpcrdma_buffer_put()`, `rpcrdma_req_setup()`, `rpcrdma_rep_create()`, and `rpcrdma_post_recvs()`. MR and regbuf support includes `rpcrdma_mrs_create()`, `rpcrdma_mrs_refresh()`, `rpcrdma_regbuf_realloc()`, and `__rpcrdma_regbuf_dma_map()`.

## Control flow
Connect begins in `rpcrdma_xprt_connect()`, which creates an endpoint and CM ID, resolves address/route, registers removal notification, queries FRWR device limits, allocates CQs, PD, and QP, posts initial Receives, calls `rdma_connect()`, waits for establishment, creates send contexts, sets up request header buffers, preallocates MRs, and creates the write-pad MR. Disconnect calls `rdma_disconnect()`, drains Receive then Send queues, unmaps reply buffers, resets requests, destroys MRs and send contexts, drops endpoint references, and destroys the CM ID when the final reference leaves. Receive completions sync the buffer and call `rpcrdma_reply_handler()`; Send completions return send contexts and may force disconnect on non-success status.

## State and persistence behavior
All state is runtime-only. `struct rpcrdma_ep` holds CM/QP/CQ/PD objects, negotiated inline thresholds, credit-related limits, completion IDs, and connection status. `struct rpcrdma_buffer` holds request objects, reply receive objects, MR lists, and the fixed-size send context ring. Registered buffers cache DMA mappings until disconnect or resize. Endpoint krefs protect resources while Receives are outstanding and during disconnect drain.

## Dependencies and integration points
This file depends on RDMA CM, IB verbs, device removal notifications, FRWR memory-registration helpers, SunRPC transport callbacks, and `rpc_rdma.c` for Reply handling and Send SGE unmapping. It is called by `transport.c` for connect/disconnect and by `rpc_rdma.c` for MR allocation, Receive reposting, and buffer management.

## Risks and edge cases
Resource lifetime is the main risk. `rpcrdma_xprt_drain()` open-codes drain order because Receive completions can schedule deferred Reply work and local invalidations. Send context ring barriers must keep producer/consumer views consistent. `rpcrdma_post_recvs()` serializes concurrent posters with `re_receiving` and must return failed WRs to the pool. CM disconnect/device removal must force SunRPC disconnect exactly once while endpoint references may still exist. MRs still on a request's registered list at reset are not reusable and are released. DMA mapping failures must not leave buffers marked mapped.

## Test signals
Coverage should include address and route resolution errors, CM rejection/unreachable/disconnect/address-change events, negotiated inline threshold changes, CQ/PD/QP allocation failures, connect followed by immediate disconnect, Receive posting under credit changes, Receive completion with invalidate, Send flush, empty send-context ring, MR pool exhaustion and refresh, regbuf resize while mapped, request/reply buffer pool cleanup, and device removal. Tracepoints for CM events, post_recv, send/receive completions, create MRs, DMA map errors, and disconnect are the best runtime signals.
