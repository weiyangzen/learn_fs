# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rqt.h

Purpose: Declares the receive queue table abstraction and RSS indirection-table storage used by mlx5e RX resources.

Important types and APIs: `struct mlx5e_rss_params_indir` holds an indirection array plus actual and maximum table sizes. `struct mlx5e_rqt` holds the mlx5 device, RQTN, and table size. The header exports direct/indirect init and redirect APIs, `mlx5e_rqt_get_rqtn()`, sizing helpers, and uniform indirection initialization.

Control flow and state: The header defines ownership boundaries but no complex logic. Callers allocate and own `mlx5e_rqt` and call the C implementation to create/destroy hardware tables. `MLX5E_INDIR_MIN_RQT_SIZE` fixes the minimum RSS RQT size at 256 entries.

Dependencies and integration: Included by `rss.h`, `rx_res.h`, and RQT users that need RQTN numbers for TIR builders. It depends on Linux kernel types and forward-declares `mlx5_core_dev`.

Risks and test signals: ABI drift between the header and `rqt.c` would break RSS and direct TIR setup. Tests should confirm all callers destroy initialized RQTs, pass table sizes matching `max_table_size`, and handle `mlx5e_rqt_size()` limits.
