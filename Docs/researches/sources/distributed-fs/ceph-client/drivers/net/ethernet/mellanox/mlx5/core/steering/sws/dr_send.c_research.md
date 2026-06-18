# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_send.c

## Purpose
`dr_send.c` is the low-level transport for writing STEs, hash tables, modify-header actions, patterns, and arguments into hardware memory. It creates a loopback RC QP/CQ pair, stages data through DMA buffers when needed, posts RDMA write/read or flow-table-access WQEs, and drains completions to keep the send queue bounded.

## Important APIs, Types, And Functions
Public APIs include `mlx5dr_send_info_pool_create()`, `mlx5dr_send_info_pool_destroy()`, `mlx5dr_send_info_alloc()`, `mlx5dr_send_info_free()`, `mlx5dr_send_fill_and_append_ste_send_info()`, `mlx5dr_send_postsend_ste()`, `mlx5dr_send_postsend_htbl()`, `mlx5dr_send_postsend_formatted_htbl()`, `mlx5dr_send_postsend_action()`, `mlx5dr_send_postsend_pattern()`, `mlx5dr_send_postsend_args()`, `mlx5dr_send_ring_alloc()`, and `mlx5dr_send_ring_free()`. Important state types are `struct mlx5dr_send_ring`, `struct mlx5dr_qp`, `struct mlx5dr_cq`, `struct mlx5dr_mr`, `struct postsend_info`, and pooled `struct mlx5dr_ste_send_info`.

## Control Flow
Send-ring allocation creates a CQ, RC QP, moves the QP through RST->INIT->RTR->RTS, allocates a staging buffer and sync buffer, and registers both as physical-address mkeys. Posts are serialized under `send_ring->lock`. Before posting, `dr_handle_pending_wc()` polls completions when the number of pending WQEs reaches the signal threshold or drains harder when the queue is near full.

ICM writes are posted as an RDMA write followed by an RDMA read into the sync buffer, giving ordering/synchronization. Modify-header arguments use `MLX5_OPCODE_FLOW_TBL_ACCESS` and are chunked by action cache line. Hash-table posts format either default STEs or existing reduced STEs plus masks, preparing each STE for the hardware format through the STE context before posting.

## State And Persistence
The file maintains RX/TX send-info pools, send queue producer/consumer accounting, CQ ownership state, `pending_wqe`, `tx_head`, `signal_th`, DMA-backed staging memory, an error-state bit, QP/CQ resources, and registered memory keys. Hardware persistence is the remote ICM or argument memory written by successful WQEs. If the device is in internal error or the ring is in error state, posts are skipped with success-like return to avoid making shutdown worse.

## Dependencies And Integration Points
It integrates with mlx5 core command APIs, work queue helpers, CQ helpers, DMA mapping, GID querying, ICM chunk address/rkey helpers, and STE preparation callbacks. `dr_rule.c`, `dr_ste.c`, `dr_ptrn.c`, and action code all rely on this file for posts. Capability fields control force-loopback QP setup, RoCE GID use, isolated VL/TC, inline size, and source UDP port.

## Risks
Queue accounting is subtle because ICM writes consume two WQEs while argument updates consume one. CQ errors set `err_state`; after that, callers may see posts skipped instead of failed. Large table writes are split by `max_post_send_size`; iteration math must match chunk sizes. Resource teardown assumes QP/CQ/MR creation reached the corresponding stage. DMA mapping and mkey creation failures need exact unwind order to avoid leaks.

## Test Signals
Useful tests include send-info pool refill/exhaustion, QP setup with and without force-loopback, CQ polling on success and error CQEs, posts with inline and staged data, table writes larger than one post, argument writes spanning multiple cache lines, and shutdown behavior during internal device error. Integration signals are successful rule/matcher hardware programming and no pending-WQE deadlock under high update rates.
