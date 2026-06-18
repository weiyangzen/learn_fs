# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xdp.h

Purpose: declares mlx5e XDP transmit/receive helpers shared by regular XDP, AF_XDP/XSK, and completion cleanup. It defines the completion FIFO payload contract for frame/page/XSK transmit modes and the inline MPWQE helpers used by the XDP SQ fast path.

Important APIs/types/functions: `enum mlx5e_xdp_xmit_mode`, `union mlx5e_xdp_info`, `struct mlx5e_xdp_wqe_info`, `mlx5e_xdp_tx_enable/disable/is_enabled/is_active`, `mlx5e_xmit_xdp_doorbell`, `mlx5e_xdp_get_inline_state`, `mlx5e_xdp_mpwqe_is_full`, `mlx5e_xdp_mpwqe_add_dseg`, and `mlx5e_xdpi_fifo_push/pop`. External entry points include `mlx5e_xdp_handle`, `mlx5e_poll_xdpsq_cq`, `mlx5e_xdp_xmit`, metadata ops, and indirect-call transmit implementations.

Control flow and state: enable/disable toggles `MLX5E_STATE_XDP_TX_ENABLED` and `MLX5E_STATE_XDP_ACTIVE`, with `synchronize_net()` on disable so remote NAPI/XSK wakeups observe the new state. Doorbells are deferred through `sq->doorbell_cseg`. Inline MPWQE mode uses FIFO outstanding depth hysteresis to move small packets inline only under HCA pressure. Completion state is stored in `sq->db.xdpi_fifo`, driven by producer/consumer counters and mode-specific trailing entries.

Dependencies and integration: depends on mlx5e channel/SQ/RQ structures, XDP core, XSK metadata, mlx5 WQE layout, and indirect-call wrappers. XSK TX and XDP CQ polling must push/pop FIFO entries in the exact documented order.

Risks and test signals: incorrect FIFO accounting causes bad unmap/free or UMEM completion; bad inline size calculations can corrupt WQEs; missing `synchronize_net()` would race with NAPI. Exercise XDP_TX, XDP_REDIRECT, AF_XDP TX with metadata, MPWQE/non-MPWQE modes, MTU boundary checks, and disable while wakeups are in flight.
