# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/mp.h

Purpose: Declares the multipath LAG control state and public lifecycle helpers used by the mlx5 LAG core.

Important APIs and types: `enum mlx5_lag_port_affinity` encodes normal, port 1, and port 2 affinity. `struct lag_mp` embeds a FIB notifier, route tracking tuple (`mfi`, priority, destination, prefix length), and the workqueue used by `mp.c`. Exports are `mlx5_lag_mp_init()`, `mlx5_lag_mp_cleanup()`, `mlx5_lag_mp_reset()`, and `mlx5_lag_is_multipath()`.

State and dependencies: The header includes `lag.h` and `mlx5_core.h`, and it is feature-gated by `CONFIG_MLX5_ESWITCH`. Without eswitch support, all functions become no-op or false inline stubs, so callers can remain unconditional.

Risks and test signals: The `mfi` pointer is intentionally stored as `const void *` for identity tracking, so implementation code must own lifetime with FIB references before dereference. Build coverage should include both eswitch-enabled and eswitch-disabled configurations, plus callers that assume init/cleanup idempotency.
