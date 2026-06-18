# subset-b-006287 research

Grouped research for Linux SUNRPC RPC/RDMA client and server files under `sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma`. Each file section is delimited for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/rpc_rdma.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/rpc_rdma.c

## Purpose
`rpc_rdma.c` implements the client-side RPC-over-RDMA protocol machinery above the RDMA verbs layer. It chooses whether each RPC Call and Reply uses inline transfer, Read chunks, Write chunks, or Reply chunks; marshals RPC/RDMA v1 transport headers; prepares Send SGEs; decodes incoming RPC/RDMA Replies; updates RPC credit grants; and completes or defers SunRPC requests after memory registration invalidation.

## Important APIs, types, and functions
The file operates on `struct rpcrdma_xprt`, `struct rpcrdma_req`, `struct rpcrdma_rep`, `struct rpcrdma_mr`, and `struct rpcrdma_xdr_cursor` from `xprt_rdma.h`. `rpcrdma_set_max_header_sizes()` computes inline payload limits after endpoint negotiation. `rpcrdma_marshal_req()` is the central outbound entry point called by `transport.c`. It uses `rpcrdma_args_inline()`, `rpcrdma_results_inline()`, and `rpcrdma_nonpayload_inline()` to choose `enum rpcrdma_chunktype` modes. `rpcrdma_encode_read_list()`, `rpcrdma_encode_write_list()`, and `rpcrdma_encode_reply_chunk()` register memory via `frwr_map()` and encode chunk descriptors. `rpcrdma_prepare_send_sges()` builds the Send WR SGE list for header, inline head, pages, and tail. On receive, `rpcrdma_reply_handler()` parses fixed headers, matches `xid` to an `rpc_rqst`, handles remote invalidation through `frwr_reminv()`, starts async local invalidation with `frwr_unmap_async()`, and eventually calls `rpcrdma_complete_rqst()`.

## Control flow
Outbound flow starts in `xprt_rdma_send_request()`, which calls `rpcrdma_marshal_req()`. The marshal path allocates sparse reply pages if needed, initializes an XDR stream over the per-request RDMA header buffer, writes `xid`, version, credit grant, and message type, chooses Read/Write/Reply chunk usage, encodes chunk lists, then prepares Send SGEs. The send itself is posted by `frwr_send()`. Inbound flow starts from `verbs.c` Receive completion, which fills an `rpcrdma_rep` and calls `rpcrdma_reply_handler()`. Reply handling decodes fixed fields, recognizes backchannel Calls when enabled, pins the matching request, updates the congestion window from server credits, records the receive context on the request, performs remote/local invalidation, and posts more Receives according to credits. Completion can happen immediately or after Send/local-invalidate completion through `kref` callbacks.

## State and persistence behavior
No persistent storage is used. Runtime state is held in per-transport statistics, `rb_credits` and `rpc_xprt.cwnd`, request-local MR lists (`rl_free_mrs`, `rl_registered`), `rl_reply`, and `rl_kref`. The kref coordinates races between Send completion and Reply completion when Send SGEs need DMA unmapping before an RPC can be finalized. MRs are moved from transport pools to requests, then released or invalidated back through FRWR helpers. Inline receive fixup can redirect `rq_rcv_buf` head/tail bases directly into the Receive buffer while copying only pagelist bytes.

## Dependencies and integration points
This file depends on Linux XDR helpers, SunRPC request lookup/completion, RPC credential flags, RPC/RDMA protocol constants, `frwr_ops.c` for memory registration/invalidation and Send posting, `verbs.c` for buffers and Receive reposting, and optional backchannel helpers. Tracepoints under `trace/events/rpcrdma.h` are the primary observability hooks. It integrates with `transport.c` through `rpcrdma_marshal_req()`, `rpcrdma_reset_cwnd()`, and completion/stat reporting.

## Risks and edge cases
Chunk selection is constrained: the implementation supports limited combinations and generally one Read or Write chunk list shape. GSS integrity/privacy disables direct data placement, forcing Reply chunks or Position Zero Read chunks. Header-buffer sizing and device `max_send_sge` limits must agree with negotiated inline thresholds. `rpcrdma_inline_fixup()` must preserve XDR padding semantics for Write chunks. Bad Reply headers wake the RPC task with status while returning status zero to SunRPC completion. Request loss, flushed completions, and outstanding registered MRs require careful invalidation or retransmission behavior.

## Test signals
Useful signals include tracepoints for marshal failures, chunk encoding, Receive reply decode errors, remote invalidation, local invalidation, inline fixup copies, and credit changes. Functional coverage should include small inline RPCs, large write Calls using Read chunks, large read Replies using Write chunks, large non-read Replies using Reply chunks, GSS DATATOUCH requests, sparse reply page allocation failures, malformed Reply chunk lists, backchannel Call detection, remote invalidation completions, Send completion racing Reply completion, and reconnect/retransmit after flushed receives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/rpc_rdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma.c

## Purpose
`svc_rdma.c` is the server-side module initialization, teardown, sysctl, and statistics entry point for the RPC/RDMA service transport. It exposes tunables for server RDMA credits and inline request sizing, owns per-CPU service counters, creates the shared `svcrdma` workqueue, and registers/unregisters the server transport class.

## Important APIs, types, and functions
Global tunables include `svcrdma_ord`, `svcrdma_max_requests`, `svcrdma_max_bc_requests`, and `svcrdma_max_req_size`. Per-CPU counters include `svcrdma_stat_read`, `svcrdma_stat_recv`, `svcrdma_stat_sq_starve`, and `svcrdma_stat_write`. `svcrdma_counter_handler()` implements sysctl read/reset behavior for counters. `svc_rdma_proc_init()` initializes counters and registers the `sunrpc/svc_rdma` sysctl table. `svc_rdma_proc_cleanup()` unregisters the table and destroys counters. `svc_rdma_init()` allocates the `svcrdma_wq` workqueue and registers `svc_rdma_class`; `svc_rdma_cleanup()` reverses this.

## Control flow
Module/service startup calls `svc_rdma_init()`. It first allocates an unbound workqueue, then initializes proc/sysctl state. Only after sysctl setup succeeds does it publish `svcrdma_wq` and register the transport class so server listeners can be created. Cleanup unregisters the transport class first to stop new users, tears down proc counters, nulls the global workqueue pointer, and destroys the old workqueue.

## State and persistence behavior
State is kernel runtime state only. Tunables live in global variables and are exposed through sysctl while the module is active. Counters are per-CPU and can be reset by writing to their sysctl entries. `svcrdma_wq` is a global workqueue used by later async cleanup paths in send and RW code. There is no disk persistence.

## Dependencies and integration points
The file depends on Linux sysctl, per-CPU counters, workqueues, and SunRPC service transport registration. It references `svc_rdma_class` from the transport implementation and is used by `svc_rdma_rw.c` and `svc_rdma_sendto.c` through the exported `svcrdma_wq` and counters. The tunables feed listener/connection setup in `svc_rdma_transport.c`.

## Risks and edge cases
Initialization order matters: `svcrdma_wq` must not be visible before sysctl setup succeeds. Error unwind in `svc_rdma_proc_init()` must destroy only counters that were initialized. Counter sysctl reads use a fixed buffer sized for unsigned long long text and return `-EFAULT` if formatting overflows. Cleanup must handle partially initialized module state and avoid destroying a NULL workqueue.

## Test signals
Tests should check module init/cleanup under allocation failures, sysctl min/max enforcement, counter reset-by-write behavior, transport class registration presence, and use-after-free absence when async work is queued before cleanup. Runtime signals are `svcrdma_stat_*` counters, debug prints, and registration failures from `svc_rdma_init()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma_backchannel.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma_backchannel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma_pcl.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma_pcl.c

## Purpose
`svc_rdma_pcl.c` builds and processes server-side parsed chunk lists. It converts raw RPC/RDMA Read, Write, and Reply chunk encodings into `struct svc_rdma_pcl` lists that later receive, read, write, and send paths use to move payloads and suppress already-written result payload regions from inline Sends.

## Important APIs, types, and functions
The main data structures are `struct svc_rdma_pcl`, `struct svc_rdma_chunk`, and `struct svc_rdma_segment`. `pcl_free()` releases all chunks in a parsed list. `pcl_alloc_call()` extracts position-zero Read segments into `rc_call_pcl`, representing long Call bodies. `pcl_alloc_read()` groups nonzero-position Read segments by XDR position into sorted chunks. `pcl_alloc_write()` constructs Write or Reply chunk lists from counted segment arrays. `pcl_process_nonpayloads()` walks an `xdr_buf` and invokes an actor only for ranges not already assigned to RDMA Write result payloads.

## Control flow
The receive decoder in `svc_rdma_recvfrom.c` first sanity-checks raw chunk lists and stores segment/chunk counts. It then calls these allocation helpers with a pointer to the raw XDR data. Read chunks are grouped by `position`; position zero is treated as Call-body data and nonzero positions are sorted. Write chunks are kept in wire order, each with a segment array and accumulated total length. Later, `svc_rdma_result_payload()` annotates Write chunks with payload positions and lengths. `svc_rdma_sendto.c` and `svc_rdma_rw.c` call `pcl_process_nonpayloads()` so inline Send or Reply-chunk construction skips payload bytes already transferred by RDMA Write, including their XDR padding.

## State and persistence behavior
The parsed lists live inside a receive context for one RPC transaction. Chunk allocation is dynamic with flexible arrays sized by segment count. Lists are freed when the receive context is returned to the context pool. There is no persistent state; `cl_count` is repurposed from raw segment/chunk count input to parsed chunk count output for Read lists.

## Dependencies and integration points
This file depends on XDR decode helpers from RPC/RDMA protocol headers, Linux list APIs, and tracepoints for segment decode visibility. It integrates with `svc_rdma_recvfrom.c` for parsing, `svc_rdma_rw.c` for Read/Write construction, and `svc_rdma_sendto.c` for reply mapping and payload exclusion.

## Risks and edge cases
Memory allocation failure aborts parsing and causes receive error handling. `pcl_alloc_read()` contains a TODO for checking chunk range overlaps; overlapping positions could confuse upper-layer reconstruction if not rejected elsewhere. `pcl_process_nonpayloads()` assumes aligned positions and total XDR lengths; incorrect `ch_payload_length` annotation could skip or double-send reply bytes. Position-zero and nonzero Read chunks are intentionally separated, so mixed special cases must be tested carefully.

## Test signals
Useful tests include Read lists with out-of-order positions, position-zero Call chunks, multiple segments per Write chunk, allocation failures, malformed segment counts rejected before allocation, payload annotations that cause head/middle/tail nonpayload processing, zero-length payload chunks, and XDR subsegment overflow. Tracepoints `trace_svcrdma_decode_rseg()` and `trace_svcrdma_decode_wseg()` confirm parsed segment content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma_pcl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma_recvfrom.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma_recvfrom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma_rw.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma_rw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma_sendto.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma_sendto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma_transport.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma_transport.c

## Purpose
`svc_rdma_transport.c` implements the server-side RPC/RDMA transport class: listener setup, RDMA CM event handling, connection acceptance, queue-pair and resource sizing, transport detachment/free, and write-space signaling. It bridges the generic SunRPC service transport interface with RDMA CM and verbs resources.

## Important APIs, types, and functions
The central exported integration object is `svc_rdma_class`, whose operations are implemented by this file and by the receive/send modules. `svc_rdma_create()` creates listener transports; `svc_rdma_accept()` accepts RDMA CM child connections and initializes `struct svcxprt_rdma`; `svc_rdma_detach()` and `svc_rdma_free()` tear down transports. `qp_event_handler()` and RDMA CM event callbacks translate provider events into service transport state. `svc_rdma_has_wspace()` reports write-space availability from SQ waiters. `svc_rdma_kill_temp_xprt()` is present as the class hook but is empty in this snapshot.

## Control flow
Listener creation binds an RDMA CM ID to the requested address and starts listening. CM connection requests create temporary transport state, negotiate private data and limits, allocate protection domain, CQs, QP, receive/send/RW context pools, and post initial Receives. `svc_rdma_accept()` promotes a queued temporary connection to a service xprt, copies peer/local addresses, initializes credit and SQ accounting, accepts the CM connection, and hands it to the SunRPC service layer. Disconnect, device removal, QP fatal, or service close paths mark the xprt closing, disconnect RDMA CM, flush receive queues, destroy contexts, and release references.

## State and persistence behavior
All state is runtime transport state: RDMA CM IDs, QPs, CQs, PDs, queue depths, credit counts, flags, locks, wait queues, and context pools. Temporary transports exist between CM request and service accept. Established transports track pending receives, send queue availability, registered context caches, and backchannel association. No disk persistence is involved.

## Dependencies and integration points
This file depends on RDMA CM, IB verbs, SunRPC `svc_xprt` lifecycle helpers, server tunables from `svc_rdma.c`, receive setup from `svc_rdma_recvfrom.c`, send context cleanup from `svc_rdma_sendto.c`, and RW context cleanup from `svc_rdma_rw.c`. It is the file that makes the other `svc_rdma_*` data-path operations reachable through the service transport class.

## Risks and edge cases
Connection negotiation must cap advertised credits and inline sizes to device and sysctl limits. Resource setup failures need precise unwind so QP/CQ/PD/CM IDs and context pools do not leak. Accept races with disconnect and device removal are high risk because temporary transports can be killed before promotion. SQ depth and receive depth must leave headroom for backchannel and batching. `svc_rdma_free()` must coordinate with completions and async work so no context is freed while provider callbacks can still run.

## Test signals
Coverage should include listener bind/listen failure, CM request rejection, accept success, private-data negotiation, low device limits, QP event errors, disconnect before accept, device removal notification, receive-post failure during setup, backchannel credit sizing, `svc_rdma_has_wspace()` under SQ pressure, and teardown with outstanding Read/Write/Send/Receive completions. Runtime evidence comes from transport class registration, RDMA CM traces, queue-depth counters, service xprt flags, and resource leak detectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma_transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/transport.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/verbs.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/verbs.c -->
