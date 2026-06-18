# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/xsk/setup.c

Purpose: builds, opens, closes, activates, and deactivates the dedicated AF_XDP receive and transmit queues for a channel.

Important APIs/types/functions: `mlx5e_validate_xsk_param`, `mlx5e_open_xsk`, `mlx5e_close_xsk`, `mlx5e_activate_xsk`, and `mlx5e_deactivate_xsk`. Local helpers validate legacy linear mode, initialize XSK RQ fields, and open the XSK RQ.

Control flow and state: validation enforces chunk size bounds and linear SKB feasibility for striding/cyclic RQs. `mlx5e_open_xsk` validates params, opens RX CQ, opens XSK RQ, opens TX CQ, then opens a separate XSK XDPSQ so pool disable can stop old CQEs cleanly. Close clears channel XSK state, synchronizes with NAPI, closes RQ/SQ/CQs, and zeroes the embedded structs. Activate/deactivate manipulate `MLX5E_RQ_STATE_ENABLED` while suspending ICOSQ recovery to avoid recovery races.

Dependencies and integration: uses mlx5e CQ/RQ/XDPSQ open helpers, XDP RXQ registration, health reporter recovery gates, and XSK pool params from `pool.c`.

Risks and test signals: open error unwinding must close CQs/RQ in reverse order; activation must not race ICOSQ recovery; separate SQ cleanup prevents stale pool completions. Test open failure injection at each step, channel reopen with XDP, XSK activate/deactivate under traffic, and close during NAPI.
