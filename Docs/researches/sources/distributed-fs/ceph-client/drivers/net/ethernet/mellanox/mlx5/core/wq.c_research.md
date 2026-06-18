# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/wq.c

## Purpose
`wq.c` implements allocation, initialization, reset, debug dumping, and destruction for mlx5 work queue memory layouts: cyclic WQs, QP send/receive WQs, completion queues, and linked-list WQs.

## Important APIs, Types, and Functions
Public helpers are `mlx5_wq_cyc_create()`, `mlx5_wq_cyc_wqe_dump()`, `mlx5_wq_cyc_reset()`, `mlx5_wq_qp_create()`, `mlx5_cqwq_create()`, `mlx5_wq_ll_create()`, `mlx5_wq_ll_reset()`, and `mlx5_wq_destroy()`. They fill `struct mlx5_wq_ctrl`, `struct mlx5_wq_cyc`, `struct mlx5_wq_qp`, `struct mlx5_cqwq`, and `struct mlx5_wq_ll` defined in `wq.h`.

## Control Flow and State
Each create path allocates a doorbell record with `mlx5_db_alloc_node()`, allocates fragmented queue memory with `mlx5_frag_buf_alloc_node()` on the requested NUMA node, initializes a fragment-buffer controller with queue stride/size fields extracted from firmware context structures, and stores `wq_ctrl->mdev` for later destruction. QP creation partitions one allocation between RQ and SQ, using an offset if the RQ occupies less than a page and a fragment-array offset otherwise. Linked-list WQs initialize every WQE's next pointer and remember the tail link for pop operations.

Reset functions zero producer counters and current size, rebuild the linked free list where relevant, and update doorbell records. `mlx5_wq_cyc_wqe_dump()` is ratelimited and dumps raw WQE bytes for diagnostics. State is in coherent/fractured queue memory, doorbell records, queue counters, and linked next pointers; no disk-persistent state exists.

## Dependencies and Integration Points
The file depends on mlx5 fragmented buffer allocation, doorbell records, generated context access macros, WQE/CQE definitions, and callers across mlx5e, core CQ/SQ handling, RDMA, and test code such as `wc.c`.

## Risks and Test Signals
Risks include mismatched log sizes/strides, wrong SQ/RQ offset math for QP queues, failure unwind leaks, stale doorbell records after reset, linked-list tail corruption, and consumers using full/missing counters inconsistently. Tests should cover mlx5 driver build, queue creation/destruction in probe/open/close paths, allocation failure injection, WQE dump paths, CQ/SQ/RQ traffic, QP layout cases with sub-page and multi-page RQ sizes, and DMA/debug checks for queue buffer access.
