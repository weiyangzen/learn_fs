# sources/distributed-fs/ceph-client/net/rds/ib_send.c

## Purpose
`ib_send.c` implements RDS/IB transmit work: normal SEND frames, RDMA READ/WRITE work requests, masked atomic operations, send completion handling, DMA unmapping, message completion notification, flow-control credit accounting, piggybacked ACK handling, and send-ring initialization/cleanup.

## Important APIs, Types, and Functions
Core functions include `rds_ib_xmit()`, `rds_ib_xmit_rdma()`, `rds_ib_xmit_atomic()`, `rds_ib_send_cqe_handler()`, `rds_ib_send_grab_credits()`, `rds_ib_send_add_credits()`, `rds_ib_advertise_credits()`, `rds_ib_send_init_ring()`, `rds_ib_send_clear_ring()`, and `rds_ib_xmit_path_complete()`. Important helpers are `rds_ib_send_unmap_op()`, `rds_ib_send_unmap_data()`, `rds_ib_send_unmap_rdma()`, `rds_ib_send_unmap_atomic()`, and `rds_ib_set_wr_signal_state()`.

## Control Flow
`rds_ib_xmit()` is called by generic send code with the connection send path serialized. It allocates enough send-ring slots for RDS_FRAG_SIZE fragmentation, optionally acquires flow-control credits, maps the data scatterlist on first use, finalizes header flags and extension headers, piggybacks any pending ACK, attaches credit advertisement if needed, builds a linked list of `ib_send_wr`s, marks selected WRs signaled, hands the message reference to the final fragment, and posts the chain with `ib_post_send()`. Partial progress is represented through `op_dmasg` and `op_dmaoff`.

`rds_ib_xmit_rdma()` maps the RDMA op SG list unless an ODP MR is supplied, allocates enough ring entries to send the entire RDMA operation, chunks SGEs according to device `max_sge`, chooses READ or WRITE opcodes, optionally uses the ODP lkey/address, and posts a WR chain. It does not support partial RDMA progress. `rds_ib_xmit_atomic()` builds a single masked atomic fetch-add or compare-swap WR, maps the 8-byte return buffer for DMA_FROM_DEVICE, and posts it.

Completion handling first separates the special ACK WR id from normal ring entries. Normal completions calculate contiguous completed entries, unmap data/RDMA/atomic resources by opcode, translate IB completion status into RDS RDMA status, wake message waiters when the final op unmapped, drop message references, free ring entries, update signaled count, requeue send work when space/credits become available, and drop the connection on unexpected errors while up.

Flow control stores send credits and posted receive credits in one atomic integer. `rds_ib_send_grab_credits()` uses `cmpxchg` to atomically reserve send credits and drain posted-credit advertisements, withholding the last credit unless it can carry a credit update. `rds_ib_send_add_credits()` receives peer credits and requeues send work. `rds_ib_advertise_credits()` accumulates locally posted receive buffers and requests an ACK when enough credits should be advertised.

## State and Persistence
Per-connection send state includes `i_send_ring`, `i_sends`, `i_data_op`, header DMA buffers, `i_signaled_sends`, `i_unsignaled_wrs`, and `i_credits`. Per-message state tracks mapped SGs, active RDMA/atomic operations, final operation, flags, extension headers, and refcounts. State is volatile kernel memory; progress survives transient send-loop exits through message and connection fields, not persistent storage.

## Dependencies and Integration Points
The file depends on IB verbs, the RDS ring helper, generic message extension/checksum helpers, `rdma.c` completion callbacks, ACK helpers in `ib_recv.c`, transport state from `ib.h`, and sysctls in `ib_sysctl.c`. It is the primary implementation behind `struct rds_transport` callbacks `xmit`, `xmit_rdma`, `xmit_atomic`, and `xmit_path_complete`.

## Risks
The send path has many rollback paths. Failed `ib_post_send()` must undo ring allocation, signaled counters, and partial final-op ownership correctly. Flow-control atomic packing is subtle and can deadlock both peers if the last-credit rule is broken. Completion relies on ordered contiguous CQEs for ring freeing. DMA mapping/unmapping direction must match op type; mistakes can corrupt payloads or completion buffers. RDMA and atomic error completion semantics are user-visible through notifier queues.

## Test Signals
Exercise normal sends across fragmentation boundaries, zero-length sends, flow-control throttling, credit advertisement piggybacking, ACK WR completion, RDMA read/write with multi-SGE and ODP cases, atomic FADD/CSWP, send-ring full rollback, CQ error statuses, and reconnect during outstanding sends. Useful counters include `s_ib_tx_cq_event`, `s_ib_tx_ring_full`, `s_ib_tx_throttle`, `s_ib_tx_sg_mapping_failure`, `s_ib_tx_credit_updates`, `s_ib_tx_stalled`, `s_send_rdma_bytes`, and `s_recv_rdma_bytes`.
