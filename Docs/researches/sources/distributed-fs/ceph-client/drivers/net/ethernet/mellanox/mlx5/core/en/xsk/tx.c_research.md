# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/tx.c

Purpose: implements AF_XDP TX wakeup and descriptor draining into mlx5e XDP SQ WQEs.

Important APIs/types/functions: `mlx5e_xsk_wakeup`, `mlx5e_xsk_tx`, and local `mlx5e_xsk_tx_post_err`.

Control flow and state: wakeup rejects inactive XDP or invalid qid, marks NAPI missed when scheduled, or posts an async ICOSQ trigger with `MLX5E_SQ_STATE_PENDING_XSK_TX`. TX loops over budget, checks SQ space through indirect-call check functions, peeks an XSK TX descriptor, builds `mlx5e_xmit_data`, syncs DMA for device, transmits through MPWQE/non-MPWQE indirect call, and pushes XSK completion metadata into the XDP info FIFO. Failed packet size/transmit posts a NOP so completions stay ordered. Flush completes MPWQE, rings the doorbell, and releases consumed TX descriptors.

Dependencies and integration: uses XSK descriptor APIs, XDP transmit functions from `xdp.h`, NAPI/ICOSQ trigger paths, and XSK TX metadata completion support.

Risks and test signals: completion FIFO order must match CQ cleanup; NOP error path must release descriptors exactly once; TX can stall if userspace does not send wakeups for consumed-but-uncompleted frames. Test wakeup inactive/active, CQ completion ordering on oversize errors, metadata-enabled TX, MPWQE and regular SQ modes, and full SQ backpressure.
