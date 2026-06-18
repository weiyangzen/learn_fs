# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/sf.h

## Purpose

`sf/sf.h` is the public internal SF manager header for mlx5 core. It declares SF hardware-table, notifier, table, and devlink port operations, with no-op stubs when `CONFIG_MLX5_SF_MANAGER` is disabled.

## Important APIs

Enabled declarations include hardware table init/cleanup/destroy and notifier init/cleanup, SF devlink table init/cleanup/notifiers, `mlx5_sf_table_empty()`, and devlink PCI SF operations for port add/delete and function state get/set. Disabled builds provide stubs for lifecycle and table-empty helpers; devlink operation prototypes are omitted because callers are normally Kconfig-gated.

## Control Flow and State

The header has no direct flow. The declared functions manage `dev->priv.sf_hw_table`, `dev->priv.sf_table`, VHCA/eswitch/blocking notifiers, and devlink SF ports.

## Dependencies and Integration Points

It includes `linux/mlx5/driver.h` and `lib/sf.h`. It is consumed by mlx5 core probe/cleanup and devlink operations that need SF manager support.

## Risks and Test Signals

Callers must not assume SF manager support when stubs are compiled. Compile both Kconfig paths, verify no unresolved devlink SF operation references in disabled builds, and test lifecycle ordering around notifiers and table cleanup in enabled builds.
