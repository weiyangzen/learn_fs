# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/qos.h

## Purpose

`qos.h` declares the mlx5 NIC QoS scheduling helper API and provides QoS-specific logging macros. It is the private interface consumed by mlx5e QoS users and implemented by `qos.c`.

## Important APIs, Types, and Functions

The header defines `MLX5_DEBUG_QOS_MASK` and wrappers `qos_err()`, `qos_warn()`, and `qos_dbg()`. It declares support/query helpers and node lifecycle functions: `mlx5_qos_is_supported()`, `mlx5_qos_max_leaf_nodes()`, `mlx5_qos_create_leaf_node()`, `mlx5_qos_create_inner_node()`, `mlx5_qos_create_root_node()`, `mlx5_qos_update_node()`, and `mlx5_qos_destroy_node()`.

## Control Flow and State

The header has no control flow or storage. Its function contracts are stateful because they create, update, and destroy firmware scheduling elements. Callers must keep returned IDs and destroy them in dependency order.

## Dependencies and Integration Points

It includes `mlx5_core.h` for `struct mlx5_core_dev` and firmware constants. The implementation depends on scheduling command helpers and QoS capability macros.

## Risks and Test Signals

Prototype drift between `qos.h` and `qos.c` is the main header-level risk. Build coverage should include mlx5e QoS users under configs where QoS is enabled and disabled, and logging should preserve the `QoS:` prefix for diagnostics.
