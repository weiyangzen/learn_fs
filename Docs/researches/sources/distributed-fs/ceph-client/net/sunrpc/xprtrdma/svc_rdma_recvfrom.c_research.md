# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma_recvfrom.c

## Purpose
`svc_rdma_recvfrom.c` is the server RPC/RDMA receive path. It manages receive-context pools, posts Receive WRs, handles Receive completions, decodes RPC/RDMA transport headers and chunk lists, detects backchannel replies, starts RDMA Reads for client-provided Read chunks, and finally presents a fully assembled RPC Call to the generic SunRPC server.

## Important APIs, types, and functions
`svc_rdma_recv_ctxt_alloc()`, `svc_rdma_recv_ctxt_get()`, `svc_rdma_recv_ctxt_put()`, and `svc_rdma_recv_ctxts_destroy()` manage receive contexts containing DMA-mapped receive buffers, parsed chunk lists, completion IDs, and pages under I/O. `svc_rdma_post_recvs()` creates enough contexts for posted Receives and in-process RPCs, then posts the initial receive set. `svc_rdma_wc_receive()` is the Receive completion handler. `svc_rdma_xdr_decode_req()` parses the fixed header, validates message type, and delegates chunk-list validation. `svc_rdma_recvfrom()` is the `xpo_recvfrom` implementation. Helper paths include `svc_rdma_read_complete_*()` for reassembling messages after RDMA Read completion.

## Control flow
Initial connection setup calls `svc_rdma_post_recvs()`, which allocates `(max_requests * 2) + recv_batch` contexts and posts `max_requests` Receive WRs. On completion, `svc_rdma_wc_receive()` refreshes the Receive Queue when below the credit target, records `wc->byte_len`, queues the context on `sc_rq_dto_q`, sets `XPT_DATA`, and enqueues the service transport. `svc_rdma_recvfrom()` first drains `sc_read_complete_q` for contexts whose RDMA Reads have finished; otherwise it pulls a fresh Receive from `sc_rq_dto_q`. It synchronizes the receive buffer for CPU access, builds `rq_arg`, decodes the RPC/RDMA header, optionally handles reverse-direction replies, computes a remote-invalidation rkey, and either returns a complete inline Call or calls `svc_rdma_process_read_list()` to post RDMA Reads and returns zero until completion.

## State and persistence behavior
Receive contexts are recycled through a lockless list and keep transaction state across the two-call Read-chunk flow. The first `svc_rdma_recvfrom()` call saves the partially built `rq_arg` in `rc_saved_arg`, moves pages from the transient `svc_rqst` into the receive context, and returns zero. The Read completion path queues the same context on `sc_read_complete_q`; a later `svc_rdma_recvfrom()` call transfers pages into a new `svc_rqst` and returns the final Call length. Parsed chunk lists and pages are released when `svc_rdma_recv_ctxt_put()` runs.

## Dependencies and integration points
This file depends on RDMA verbs Receive posting, SunRPC service queue flags, `svc_rdma_pcl.c` for parsed chunk lists, `svc_rdma_rw.c` for RDMA Read execution, `svc_rdma_sendto.c` for RDMA_ERROR responses, and `svc_rdma_backchannel.c` for reverse-direction Reply handling. It updates `svcrdma_stat_recv` and uses many `trace_svcrdma_*` decode and completion tracepoints.

## Risks and edge cases
Header parsing must reject unsupported versions, unexpected procedures, truncated lists, unaligned Read positions, oversized segment counts, and receive-buffer overflows before allocating chunks. Receive-post failure after a successful Receive intentionally drops that RPC and closes the connection to avoid replay ambiguity. Remote invalidation is used only when all chunks have one distinct rkey. Page ownership is delicate: pages are moved between `svc_rqst` and receive contexts to avoid double-free while RDMA Reads are outstanding. `XPT_DATA` must be cleared only when both receive queues are empty.

## Test signals
Coverage should include inline Calls, RDMA_MSG with one Read data item, multiple Read chunks, RDMA_NOMSG/PZRC long Calls, malformed fixed headers, bad version, bad procedure, invalid chunk lists, remote invalidation rkey selection, Receive flush/error completion, Receive Queue refresh failure, backchannel reply detection, and page handoff after Read completion. Runtime signals are receive counters, `XPT_DATA` behavior, `sc_pending_recvs`, decode tracepoints, and connection close events.
