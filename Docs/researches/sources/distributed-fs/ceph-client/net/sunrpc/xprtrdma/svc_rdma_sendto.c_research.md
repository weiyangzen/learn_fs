# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma_sendto.c

## Purpose
`svc_rdma_sendto.c` is the server RPC/RDMA transmit path. It allocates and recycles send contexts, manages Send Queue capacity with fair ticketing, maps or linearizes Reply XDR buffers for RDMA Send, encodes RPC/RDMA Reply headers, posts Send WR chains, sends RDMA_ERROR messages, and records result payload ranges for Write chunks.

## Important APIs, types, and functions
`svc_rdma_send_ctxt_get()`, `svc_rdma_send_ctxt_put()`, and `svc_rdma_send_ctxts_destroy()` manage `struct svc_rdma_send_ctxt` objects with a persistent DMA-mapped transport-header buffer and SGE array. `svc_rdma_sq_wait()` reserves SQ slots with ticket fairness; `svc_rdma_wake_send_waiters()` returns slots on completion; `svc_rdma_post_send()` posts the WR chain. Header encoding helpers include `svc_rdma_encode_read_list()`, `svc_rdma_encode_write_list()`, and `svc_rdma_encode_reply_chunk()`. `svc_rdma_map_reply_msg()` maps nonpayload Reply data or pulls it into the header buffer. `svc_rdma_sendto()` is the main `xpo_sendto` implementation.

## Control flow
When the upper RPC server has a reply, `svc_rdma_sendto()` obtains a send context, reserves fixed header space, prepares Write-list WRs for result payloads, optionally prepares a Reply chunk, writes the fixed RPC/RDMA header with credits and message type, encodes chunk lists, maps the remaining inline Reply content, moves reply pages into the send context, chooses Send With Invalidate if `rc_inv_rkey` is set, and posts the chain. Send completion returns SQ entries, releases pages and DMA mappings, recycles the send context, and closes the xprt on error. Error response flow uses `svc_rdma_send_error_msg()` to send `rdma_error` with `err_vers` or `err_chunk`, resetting the WR chain so only the error Send is posted.

## State and persistence behavior
Send contexts are pooled on a lockless list and can allocate fresh contexts on demand. Each context keeps pages transferred from `svc_rqst` so they survive after `svc_rdma_sendto()` returns. SQ availability, ticket head/tail counters, and wait queues live on `struct svcxprt_rdma`. The transport-header buffer remains DMA-mapped until context destruction; other mapped SGEs are unmapped when the context is released on the workqueue.

## Dependencies and integration points
This file depends on RDMA verbs, XDR helpers, `svc_rdma_pcl.c` for nonpayload processing, `svc_rdma_rw.c` for prepared Write/Reply chunks, server receive contexts from `svc_rdma_recvfrom.c`, and global workqueue/counters from `svc_rdma.c`. It is also used by `svc_rdma_backchannel.c` to send reverse-direction Calls.

## Risks and edge cases
The SQ ticket invariant is critical: every waiter must advance `sc_sq_ticket_tail` exactly once, including close/error paths. `svc_rdma_post_send_err()` must distinguish partial posting from complete failure to avoid double-releasing SQ slots. Pull-up decisions balance small copy cost against SGE exhaustion; incorrect nonpayload processing can duplicate bytes already sent by Write chunks. Reply chunk errors after Write WRs are prepared require saving pages before sending RDMA_ERROR so completion can release them. Send With Invalidate is skipped for error messages and used for normal replies only when safe.

## Test signals
Tests should exercise inline replies, replies with Write chunks, replies with Reply chunks, pull-up threshold behavior, maximum-SGE fallback, DMA map failure unwinding, SQ starvation fairness, partial `ib_post_send()` failure, Send flush completion, RDMA_ERROR for bad chunks/version, result payload annotation via `svc_rdma_result_payload()`, and backchannel send reuse. Tracepoints around SQ wait/post, DMA map/unmap, pull-up, Send completion, and error sends provide runtime evidence.
