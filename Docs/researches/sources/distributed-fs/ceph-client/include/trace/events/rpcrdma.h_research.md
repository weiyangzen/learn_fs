# sources/distributed-fs/ceph-client/include/trace/events/rpcrdma.h

Purpose: Defines the largest RPC/RDMA trace surface, covering client connection management, send/receive completions, memory registration, chunk marshalling, reply decoding, callback setup, server accept/decode/encode/DMA/sendqueue paths, and RDMA device notifications.

Important APIs/types/functions: Event classes include completion, send/receive flush, MR completion, receive success, reply, transport, connection, read/write chunk, MR, callback, server accept, bad request, DMA map, post chunk, sendqueue, client device, and client registration classes. Events cover `xprtrdma_inline_thresh`, connect/disconnect/device removal, MR creation/no-MR errors, read/write/reply chunks, marshal/failure/prepsend, post send/recv, FRWR alloc/dereg/map errors, reply/error/fixup/decode-seg/MR zap, callback setup/call/reply, server accept errors, request decode and short/bad request errors, segment encode/decode, DMA map/unmap/errors, send pullup/send/post/completions, read/write/reply completions, QP errors, SQ full/retry/post errors, and client add/remove/register notifications.

Control flow: Client xprtrdma emits events through connection negotiation, request marshalling, chunk list construction, send/receive posting, CQ completions, memory registration/local invalidation, reply decode, and callback handling. Server svcrdma emits events through RDMA accept, request header decode, chunk segment decode/encode, DMA mapping, send context posting, completion handling, queue pressure, and device removal.

State and persistence: No state is owned. It observes `rpcrdma_xprt`, endpoints, requests, replies, MRs, RDMA CIDs, work completions, CQs, QPs, DMA addresses, chunks, server contexts, and RDMA devices. Persistent NFS/RPC data is outside this header; RDMA resources persist only until deregistration/disconnect.

Dependencies and integration points: Depends on scatterlist, SUNRPC RDMA CID definitions, RDMA CM/verbs, and trace misc helpers for RDMA/SUNRPC. It integrates with NFS over RDMA client/server, RDMA providers, DMA mapping, and RPC transport diagnostics.

Risks and test signals: Risks include object lifetime races in CQ callbacks, exposing DMA addresses/remote keys, endian mistakes in RPC/RDMA header decoding, MR leak or invalidation imbalance, sendqueue credit bugs, provider-specific WC statuses, and trace overhead on high-throughput RDMA. Test NFS/RDMA mount/read/write, krb5 over RDMA where supported, connection loss/reconnect/device removal, FRWR registration failure, remote invalidation, malformed RPC/RDMA headers, SQ exhaustion, CQ error completions, server read/write/reply chunks, and provider unload.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/rpcrdma.h` completely for this pass (2341 lines, 51394 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/rpcrdma.h_research.md`.
