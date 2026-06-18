# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/wr.c

## Purpose
`wr.c` implements mlx5 RDMA send and receive posting for QPs. It converts RDMA core work requests into mlx5 WQE control, address, datagram, Ethernet/LSO, data, UMR, memory-registration, local-invalidate, and integrity-signature segments, maintains software queue state, and rings hardware doorbells.

## Important APIs, types, and functions
Public entry points are `mlx5_ib_post_send()`, `mlx5_ib_post_recv()`, `mlx5r_wq_overflow()`, `mlx5r_begin_wqe()`, `mlx5r_finish_wqe()`, and `mlx5r_ring_db()`. Helpers map IB opcodes to mlx5 opcodes, fill remote-address and SGE data segments, copy inline payloads across fragmented SQ edges, build UD/GSI address vectors, build Ethernet LSO/checksum segments, construct UMR segments for fast-reg and local invalidate, configure protection-information BSF/PSV state, and compute optional WQE signatures.

## Control flow
`mlx5_ib_post_send()` rejects non-drain posts during internal device error, delegates GSI posts, locks the SQ, validates opcode and SGE count, begins each WQE, chooses fence mode, dispatches QP-type-specific segment construction, appends inline or SGE data segments, records WR metadata, finishes WQE sizing/indexing, and rings one doorbell for all accepted WQEs. RC/XRC sends handle RDMA, local invalidate, MR registration, and integrity registration; UC handles RDMA writes; UD/GSI writes datagram segments and optional IPoIB offload headers. `mlx5_ib_post_recv()` similarly locks the RQ, validates space/SGEs, fills receive scatter entries, terminates unused SGEs with the terminate lkey, optionally signs the receive WQE, records WR IDs, updates the RQ head, and writes the receive doorbell record.

## State and persistence
The file updates volatile QP SQ/RQ state: head/tail-derived overflow checks, `cur_post`, `cur_edge`, WR IDs, WQE head/next metadata, opcode records, fence carry state, receive head, and doorbell records. Persistent device-visible state is the WQE memory and doorbell writes consumed by the HCA. Integrity registration also changes signature MR bookkeeping such as `sig_status_checked` and `next_fence`.

## Dependencies and integration points
It depends on RDMA core WR structures, mlx5 hardware WQE layouts, `mlx5_ib_qp`, fragmented SQ buffers, BF register mappings, GSI helpers, UMR declarations from `umr.h`, memory-registration structures, and CQ locking for overflow rechecks. The completion path later interprets the WR metadata populated here.

## Risks
This is a high-risk fast path: queue overflow checks race CQ progress and depend on CQ locking; WQE construction must handle fragmented SQ edges exactly; inline LSO and integrity layouts have strict alignment; `nreq` batching means errors after previous WQEs still ring accepted work; fence state is subtle across UMR and PSV WQEs; unsupported atomics return `-EOPNOTSUPP`; and doorbell ordering relies on memory barriers and SQ locking. Any size miscalculation can corrupt adjacent WQEs.

## Test signals
Cover RC/UC/UD/XRC/SMI/GSI posting, chained WRs with mid-chain failure, max SGE and max inline boundaries, fragmented SQ edge crossing, IPoIB LSO and checksum offload, local invalidate, fast-reg MR with inline and DMA descriptors, integrity MR with and without separate PI MR, PSV updates, drain behavior during internal device error, receive zero-length and max-SGE WQEs, signature-enabled QPs, and lockdep/KASAN stress under concurrent CQ polling.
