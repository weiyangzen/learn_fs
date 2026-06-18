# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/mpesw.h

Purpose: Declares MPESW state and entry points for enabling/disabling multiport e-switch LAG and reacting to related events.

Important APIs and types: `struct lag_mpesw` stores pending work and per-port PF metadata IDs. `enum mpesw_op` distinguishes enable and disable requests. `struct mlx5_mpesw_work_st` carries queued work, completion, operation, target LAG, and result. Public APIs include `mlx5_lag_mpesw_enable()`, `mlx5_lag_mpesw_disable()`, `mlx5_lag_is_mpesw()`, `mlx5_lag_mpesw_do_mirred()`, plus eswitch-gated `mlx5_lag_disable_mpesw()`, `mlx5_mpesw_speed_update_work()`, and `mlx5_lag_mpesw_port_change_event()`.

State and dependencies: Includes LAG and mlx5 core definitions; event helpers compile to no-ops when `CONFIG_MLX5_ESWITCH` is disabled. The work-state struct makes the public enable/disable calls synchronous over an internal LAG workqueue.

Risks and test signals: Callers must not assume MPESW support when the eswitch feature is absent; build tests need both config branches. Runtime tests should verify that completion result propagation and metadata array cleanup match the implementation contract.
