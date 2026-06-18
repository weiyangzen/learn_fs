# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma_rw.c

## Purpose
`svc_rdma_rw.c` uses the kernel RDMA R/W API to execute server-side RDMA Reads and Writes for RPC/RDMA chunks. It constructs `rdma_rw_ctx` chains over `xdr_buf` and page-backed buffers, accounts for Send Queue entries, handles Read/Write/Reply chunk completions, and releases DMA resources asynchronously where completion ordering requires it.

## Important APIs, types, and functions
`struct svc_rdma_rw_ctxt` wraps one `rdma_rw_ctx` plus a bvec array. `svc_rdma_get_rw_ctxt()` and `svc_rdma_destroy_rw_ctxts()` manage a reusable context cache. `svc_rdma_cc_init()` and `svc_rdma_cc_release()` manage `struct svc_rdma_chunk_ctxt` chains. `svc_rdma_prepare_write_list()` and `svc_rdma_prepare_reply_chunk()` construct outbound Write and Reply chunk WRs. `svc_rdma_process_read_list()` builds and posts inbound RDMA Read WRs. Completion handlers are `svc_rdma_write_done()`, `svc_rdma_reply_done()`, and `svc_rdma_wc_read_done()`.

## Control flow
Write flow starts when `svc_rdma_sendto()` has an RPC Reply and parsed Write or Reply chunks. For result payload Write chunks, `svc_rdma_prepare_write_chunk()` extracts the payload subsegment, builds Writes over head/pages/tail via `svc_rdma_xb_write()`, links the WRs ahead of the final Send, and stores `svc_rdma_write_info` on the send context for later cleanup. Reply chunks use `pcl_process_nonpayloads()` to write the whole Reply except payload regions already handled by Write chunks. Read flow starts in `svc_rdma_recvfrom()` when Read chunks are present. `svc_rdma_process_read_list()` chooses one data-item Read, multiple Read chunks with copied inline gaps, or a position-zero Call chunk, builds RDMA Read contexts over request pages, moves those pages into the receive context, posts the chain, and returns until Read completion requeues the receive context.

## State and persistence behavior
R/W contexts are runtime-only cached objects on `rdma->sc_rw_ctxts`. Each chunk context owns a list of active R/W contexts and an SQE count. Write resources can outlive `svc_rdma_sendto()` because Write WRs are chained before a final Send; cleanup is delayed until Send completion via `svc_rdma_write_chunk_release()` and `svc_rdma_reply_chunk_release()`. Read resources live in the receive context until `svc_rdma_wc_read_done()` either queues a completed Call or releases resources on error.

## Dependencies and integration points
The file depends on `<rdma/rw.h>`, bvec helpers, overflow checks, SunRPC XDR buffers, `svc_rdma_pcl.c` for parsed chunks, `svc_rdma_sendto.c` for SQ waiting and Send waiters, and `svc_rdma_recvfrom.c` for receive-context handoff. It updates `svcrdma_stat_read` and `svcrdma_stat_write` and uses RDMA tracepoints for DMA map and completion diagnostics.

## Risks and edge cases
The code must prevent SQ overflow by comparing `cc_sqecount` with `sc_sq_depth` and by reserving SQ slots before posting. Page accounting is subtle: contiguous high-order allocations are split, partially used pages stay reusable, and only payload pages are moved to receive contexts. `svc_rdma_read_chunk_range()` must correctly split Call chunks around normal Read chunks. Write chunk overflow returns `-E2BIG`, which can generate an RDMA_ERROR instead of silently truncating. Completion failures close the connection because the peer cannot trust partially transferred data.

## Test signals
Tests should cover inline gaps around multiple Read chunks, position-zero Read chunks, page-list overrun, contiguous allocation success and fallback, DMA mapping failures, SQ starvation, Write chunk too small, Reply chunk too small, Write/Reply completion flushes, Read completion flushes, and cleanup after partial WR construction failure. Tracepoints plus `svcrdma_stat_read`, `svcrdma_stat_write`, and SQ wait counters are key observability signals.
