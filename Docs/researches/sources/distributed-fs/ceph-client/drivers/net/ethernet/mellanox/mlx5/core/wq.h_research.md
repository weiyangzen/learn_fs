# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/wq.h

## Purpose
`wq.h` is the shared mlx5 work queue API and inline cursor library. It declares queue allocation helpers and defines fast-path operations for cyclic WQs, completion WQs, and linked-list WQs.

## Important APIs, Types, and Functions
Core types are `struct mlx5_wq_param`, `struct mlx5_wq_ctrl`, `struct mlx5_wq_cyc`, `struct mlx5_wq_qp`, `struct mlx5_cqwq`, and `struct mlx5_wq_ll`. Inline APIs expose size, full/empty/missing tests, producer/consumer counter conversion, WQE/CQE pointer lookup, doorbell record updates, push/pop operations, wrap-count ownership checks, enhanced CQE validity checks, and linked-list next-pointer operations.

## Control Flow and State
The header has no top-level runtime flow, but its inlines are fast-path control flow. Cyclic WQs use `wqe_ctr` and `cur_sz` to derive head and tail through a power-of-two mask. CQ WQs use `cc` and owner/validity bits to decide whether hardware has produced a CQE, then issue `dma_rmb()` before returning readable contents. Linked-list WQs use `head`, `tail_next`, `wqe_ctr`, and `cur_sz` so software can push posted WQEs and relink completed/free entries.

## Dependencies and Integration Points
It depends on mlx5 IFC structures, CQ/QP definitions, fragment-buffer helpers, byte-order conversion, DMA barriers, and WQE structures such as `struct mlx5_wqe_srq_next_seg`. It is included by mlx5 core, Ethernet, RDMA, and test code that owns queue objects.

## Risks and Test Signals
Risks are concentrated in wrap arithmetic and ordering: off-by-one full checks, 16-bit cyclic counter comparisons, CQE ownership validation, missing DMA barriers, 128-byte CQE pointer adjustment, and linked-list relinking. Build coverage catches prototype drift, while runtime signals include clean TX/RX/CQ operation under wraparound, CQ overrun absence, no stale CQE reads on weakly ordered CPUs, and queue state correctness after reset.
