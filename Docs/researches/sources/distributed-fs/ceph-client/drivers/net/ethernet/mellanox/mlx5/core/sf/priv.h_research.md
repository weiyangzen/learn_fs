# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/priv.h

## Purpose

`sf/priv.h` is the private cross-file interface for mlx5 SF management. It declares command wrappers, software-to-hardware id translation, and hardware table allocation/free helpers used inside the SF subsystem.

## Important APIs

Declarations include `mlx5_cmd_alloc_sf()`, `mlx5_cmd_dealloc_sf()`, `mlx5_cmd_sf_enable_hca()`, `mlx5_cmd_sf_disable_hca()`, `mlx5_sf_sw_to_hw_id()`, `mlx5_sf_hw_table_sf_alloc()`, `mlx5_sf_hw_table_sf_free()`, `mlx5_sf_hw_table_sf_deferred_free()`, and `mlx5_sf_hw_table_supported()`.

## Control Flow, State, and Dependencies

The header has no logic or storage. The declared functions mutate firmware SF allocation/HCA state and driver hardware-table state in `dev->priv.sf_hw_table`. It depends on `linux/mlx5/driver.h` for `struct mlx5_core_dev`.

## Risks and Test Signals

Because this is an internal header, risks are prototype drift and accidental use outside intended SF layering. Build coverage should ensure `cmd.c`, `hw_table.c`, and `devlink.c` remain synchronized.
