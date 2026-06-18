# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/xprt_rdma.h

## Purpose
This header is the private contract for the SUNRPC RPC/RDMA client transport. It defines the endpoint, registered buffer, request, reply, memory registration, send context, statistics, and transport objects shared by xprtrdma implementation files such as `verbs.c`, `frwr_ops.c`, `rpc_rdma.c`, `transport.c`, and backchannel code.

## Important APIs, Types, And Functions
Key types are `struct rpcrdma_ep` for RDMA CM/verbs endpoint state, `struct rpcrdma_regbuf` for DMA mapped kmalloc buffers, `struct rpcrdma_rep` for receive completions and reply XDR state, `struct rpcrdma_sendctx` for send completion unmap metadata, `struct rpcrdma_mr` for on-demand registered memory regions, `struct rpcrdma_req` for each RPC slot, `struct rpcrdma_buffer` for transport-wide request/reply/MR pools, `struct rpcrdma_stats`, and `struct rpcrdma_xprt`. Inline helpers expose DMA address/length/lkey/device, request-to-RDMA container conversion, MR list push/pop, regbuf mapping checks, data direction selection, and XDR length reset.

## Control Flow
The header ties together endpoint connection setup, receive posting, request allocation, buffer recycling, memory registration, RPC/RDMA marshalling, send SGE preparation, reply completion, transport address formatting, close/stats, and optional backchannel functions. A request moves through `rpcrdma_marshal_req()`, FRWR mapping, send SGE construction, send completion unmapping, reply handling, and request unpin/completion.

## State And Persistence
State is in memory only. `rpcrdma_xprt` embeds the generic `rpc_xprt`, endpoint pointer, reusable buffer pool, delayed connect worker, timeout profile, and counters. Endpoint state tracks RDMA CM id, PD, QP attributes, inline limits, negotiated connection private data, receive/send batching, completion id accounting, and force-disconnect flags.

## Dependencies And Integration Points
The file depends on RDMA CM, IB verbs, SUNRPC client and RPC/RDMA protocol headers, XDR buffers, workqueues, wait queues, krefs, atomics, and optional SUNRPC backchannel. It is consumed by the RPC transport class registered by xprtrdma and by NFS/RPC users that select RDMA transports.

## Risks And Test Signals
Correctness risks cluster around DMA mapping lifetimes, FRWR invalidation ordering, negotiated inline sizes, receive batching, MR recycling, and backchannel WR provisioning. The source snapshot also shows suspicious duplicated tokens in this header, including a duplicated `enum {` near receive batching and a duplicated return in `rpcrdma_addrstr()`, which are build-quality signals to verify against the intended upstream baseline. Test signals include successful kernel build with RPC/RDMA enabled, RDMA mount/connect/reconnect tests, NFS over RDMA I/O with read/write/reply chunks, backchannel callback traffic, forced disconnect recovery, and stats counters changing under load.
