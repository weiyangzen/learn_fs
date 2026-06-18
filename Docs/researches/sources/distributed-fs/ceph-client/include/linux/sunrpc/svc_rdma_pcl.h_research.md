# sources/distributed-fs/ceph-client/include/linux/sunrpc/svc_rdma_pcl.h

Purpose: defines parsed RPC/RDMA chunk list structures and helpers used by the server receive path.

Important APIs and types: `struct svc_rdma_segment` stores handle, length, and offset. `struct svc_rdma_chunk` links a chunk, position, length, payload length, segment count, and flexible segment array. `struct svc_rdma_pcl` stores count and chunk list head. Helpers initialize lists, test emptiness, fetch first/next chunks, iterate chunks/segments, and compute aligned end offsets with `xdr_align_size()`. Allocation/process APIs include `pcl_free()`, `pcl_alloc_call()`, `pcl_alloc_read()`, `pcl_alloc_write()`, and `pcl_process_nonpayloads()`.

Control flow: the RDMA receive parser builds call/read/write/reply parsed chunk lists from incoming XDR, service RDMA code iterates chunks and segments to move payload or process non-payload data, then frees the parsed lists.

State and persistence: parsed chunk lists are per-receive-context runtime state.

Dependencies and integration points: depends on kernel lists and SUNRPC XDR alignment; integrates tightly with `svc_rdma_recv_ctxt` in `svc_rdma.h`.

Risks and test signals: risks include zero segment counts breaking iteration, malformed lengths/positions, alignment mistakes, allocation failure cleanup, and nonpayload processing gaps. Test with malformed chunk lists, multi-segment chunks, empty lists, read/write/reply chunk combinations, and KASAN.
