# sources/distributed-fs/ceph-client/include/linux/sunrpc/svc_rdma.h

Purpose: declares the server-side RPC/RDMA transport implementation state, context pools, statistics, and send/receive/read/write helper entry points.

Important APIs and types: module parameters/stats include `svcrdma_ord`, max request settings, `svcrdma_wq`, and percpu counters. `struct svcxprt_rdma` embeds `svc_xprt` and owns RDMA CM/QP/CQ/PD state, send queue accounting, credits, locks, wait queues, context freelists, receive/read completion queues, flags, and completion IDs. `struct svc_rdma_recv_ctxt` stores receive WR/CQE/SGE, receive buffer stream, invalidation key, read-pull state, saved arg buffer, parsed chunk lists, and request pages. `struct svc_rdma_send_ctxt`, `svc_rdma_write_info`, and `svc_rdma_chunk_ctxt` track send work, write/reply chunks, pages, SGE construction, and RDMA read/write completions.

Control flow: receives are posted, incoming RDMA messages are parsed into chunk lists, read chunks may be pulled into request pages, service code processes the RPC, then write/reply chunks are mapped and send WRs are posted. SQ wait/ticketing and completion IDs coordinate resource use and diagnostics.

State and persistence: transport state is connection-lifetime RDMA runtime state: credits, contexts, queues, counters, posted WRs, and pages. Nothing persists beyond the connection/service.

Dependencies and integration points: integrates SUNRPC service transport, XDR, socket service helpers, RPC/RDMA wire helpers, RDMA core verbs/CM, notification API, parsed chunk lists, workqueues, and percpu counters.

Risks and test signals: risks include SQ starvation, credit accounting bugs, DMA mapping leaks, page ownership mistakes, malformed chunk parsing, send-with-invalidate compatibility, and RDMA device removal races. Test with NFS/RDMA server workloads, read/write/reply chunks, backchannel, CQ errors, hot-unplug, and RDMA resource exhaustion.
