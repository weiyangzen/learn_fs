# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sh_devlink.h

## Purpose

`sh_devlink.h` declares the mlx5 shared-devlink lifecycle hooks used by core probe and cleanup code.

## Important APIs

It declares `mlx5_shd_init(struct mlx5_core_dev *dev)` and `mlx5_shd_uninit(struct mlx5_core_dev *dev)`.

## Control Flow, State, and Dependencies

The header has no logic or storage. The implementation stores a shared devlink pointer in `dev->shd` for PF devices with VPD serial data. It includes `linux/mlx5/driver.h` for `struct mlx5_core_dev`.

## Risks and Test Signals

Header risk is limited to prototype drift and Kconfig/build inclusion. Compile users of the hooks and test PF/VF/SF probe paths to ensure only PFs acquire shared devlink state.
