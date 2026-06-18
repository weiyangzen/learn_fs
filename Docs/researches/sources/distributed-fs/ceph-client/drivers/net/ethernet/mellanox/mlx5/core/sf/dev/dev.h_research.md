# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/dev/dev.h

## Purpose

`sf/dev/dev.h` declares the auxiliary-device representation of an mlx5 subfunction and the lifecycle hooks for SF device discovery and the SF auxiliary driver.

## Important APIs and Types

When `CONFIG_MLX5_SF` is enabled, `struct mlx5_sf_dev` embeds `struct auxiliary_device` and stores parent mdev, child mdev, SF BAR base, user SF number, and hardware function id. `struct mlx5_sf_peer_devlink_event_ctx` carries function id, devlink pointer, and error status for parent/peer devlink association. The header declares notifier/table lifecycle functions, driver register/unregister functions, and `mlx5_sf_dev_allocated()`.

When SF support is disabled, all lifecycle functions become no-ops, registration returns success, and `mlx5_sf_dev_allocated()` returns false.

## State, Dependencies, and Integration

The header depends on `linux/auxiliary_bus.h` in enabled builds and bridges `sf/dev/dev.c`, `sf/dev/driver.c`, and parent SF/devlink code. State is in the concrete structs owned by the implementation.

## Risks and Test Signals

Callers must tolerate the no-op stub behavior in non-SF builds. Compile both Kconfig paths and verify that `MLX5_SF_DEV_ID_NAME` matches the auxiliary driver id table and generated device names.
