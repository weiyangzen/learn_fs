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
