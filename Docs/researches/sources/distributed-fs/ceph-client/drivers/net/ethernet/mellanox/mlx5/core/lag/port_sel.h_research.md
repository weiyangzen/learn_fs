# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/port_sel.h

Purpose: Declares data structures and lifecycle functions for LAG port-selection flow steering.

Important APIs and types: `struct mlx5_lag_definer` groups a firmware match definer, flow table, flow group, and rule array sized by `MLX5_MAX_PORTS * MLX5_LAG_MAX_HASH_BUCKETS`. `struct mlx5_lag_ttc` pairs a TTC table with per-traffic-type definers. `struct mlx5_lag_port_sel` stores the selected traffic-type bitmap, tunnel flag, and outer/inner TTC state. Public calls are create, modify, and destroy.

State and dependencies: The header depends on `lib/fs_ttc.h` for traffic type constants and TTC table declarations. Under non-eswitch builds, port-selection APIs are no-op stubs returning success.

Risks and test signals: The rule array relies on stable LAG bucket limits and one-indexed `ports[]` values from implementation code. Compile coverage should include `CONFIG_MLX5_ESWITCH` on/off, and runtime validation should confirm create/modify/destroy calls are balanced by LAG mode transitions.
