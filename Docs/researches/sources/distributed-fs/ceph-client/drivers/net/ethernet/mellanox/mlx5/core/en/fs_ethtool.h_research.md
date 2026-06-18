# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/fs_ethtool.h

## Purpose

`en/fs_ethtool.h` declares ethtool RX flow classification/steering helpers for mlx5e, with stubs when RXNFC support is disabled.

## Important APIs, Types, and Functions

With `CONFIG_MLX5_EN_RXNFC`, it declares allocation/free, steering init/cleanup, RXFH field get/set, and RXNFC get/set helpers. Without the option, allocation returns success, cleanup/init are no-ops, and operational get/set functions return `-EOPNOTSUPP`.

## Control Flow

Flow steering setup uses alloc/init hooks, ethtool ops call get/set helpers, and teardown calls cleanup/free. Stubs allow common code to compile without feature conditionals.

## State and Persistence Behavior

The hidden `struct mlx5e_ethtool_steering` stores ethtool steering state when enabled. Disabled builds do not allocate or persist state.

## Dependencies and Integration Points

Integrates with mlx5e flow steering, ethtool RXNFC/RXFH APIs, and `struct mlx5e_priv`.

## Risks and Edge Cases

- Disabled builds make allocation appear successful but later operations unsupported; callers must not treat allocation success as feature availability.
- RXFH field changes must align with hardware/TTC hash capabilities in the implementation.

## Test Signals

Compile with and without RXNFC. Run `ethtool -n/-N` and RXFH field operations, including unsupported configuration paths in disabled builds.
