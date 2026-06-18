<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/core.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/core.h

## Purpose

This header defines the internal FPGA device object, logging helpers, and public mlx5-core FPGA lifecycle hooks. It also supplies no-op inline stubs when `CONFIG_MLX5_FPGA` is disabled.

## Important APIs, types, and functions

- `struct mlx5_fpga_device` contains the parent mlx5 core device, FPGA error notifier blocks, `state_lock`, current software state, last admin/oper images, and shared connection resources (`pdn`, `mkey`, `uar`).
- Logging macros prefix messages with `FPGA:` and, for debug/warn/error variants, include function, line, and pid.
- Lifecycle prototypes are `mlx5_fpga_init()`, `mlx5_fpga_cleanup()`, `mlx5_fpga_device_start()`, and `mlx5_fpga_device_stop()`.
- The disabled-config branch makes all lifecycle hooks harmless no-ops returning success.

## Control flow

The header has no runtime control flow except its compile-time `CONFIG_MLX5_FPGA` split. That split allows core mlx5 code to call FPGA hooks unconditionally without requiring FPGA support in the build.

## State and persistence

State is runtime-only and centered on `struct mlx5_fpga_device`. The `state_lock` is the synchronization point for state transitions observed by startup, shutdown, and error event handling.

## Dependencies and integration points

The enabled path includes mlx5 EQ/core headers and `fpga/cmd.h`. The struct is consumed by `core.c`, `conn.c`, and `sdk.c`. The no-op stubs integrate with generic mlx5 device init/cleanup paths in configurations without FPGA support.

## Risks

Any fields added to `struct mlx5_fpga_device` must be initialized in `core.c` allocation/start paths and released in cleanup paths. Logging macros dereference `(__adev)->mdev`, so they require a fully initialized FPGA object. Stub behavior must remain semantically acceptable to callers that expect FPGA absence to be non-fatal.

## Test signals

Build both with and without `CONFIG_MLX5_FPGA`. Runtime tests should assert that generic mlx5 init works on devices without FPGA capability and that enabled builds initialize, start, stop, and clean up FPGA state without leaking connection resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/core.h -->
