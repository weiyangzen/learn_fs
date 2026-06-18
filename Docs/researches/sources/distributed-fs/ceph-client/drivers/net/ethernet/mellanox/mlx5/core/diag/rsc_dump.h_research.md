# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/rsc_dump.h

## Purpose

`rsc_dump.h` declares the mlx5 resource dump lifecycle and command iteration API used by health reporters and diagnostics.

## Important APIs, Types, and Functions

- `MLX5_RSC_DUMP_ALL` is a wildcard/count constant for dump requests.
- Forward declarations hide `struct mlx5_rsc_dump` and `struct mlx5_rsc_dump_cmd`.
- Lifecycle: `mlx5_rsc_dump_create()`, `mlx5_rsc_dump_destroy()`, `mlx5_rsc_dump_init()`, `mlx5_rsc_dump_cleanup()`.
- Command API: `mlx5_rsc_dump_cmd_create()`, `mlx5_rsc_dump_cmd_destroy()`, `mlx5_rsc_dump_next()`.

## Control Flow

Callers create and initialize device-level dump support, then for each dump allocate a command from `struct mlx5_rsc_key`, call `next()` until it returns zero, and destroy the command.

## State and Persistence Behavior

The API owns hidden per-device state and per-command continuation state. Callers own pages passed to `mlx5_rsc_dump_next()`.

## Dependencies and Integration Points

Depends on `<linux/mlx5/rsc_dump.h>`, core driver headers, and `mlx5_core.h`. It integrates with Ethernet health dump helpers and firmware debug resource support.

## Risks and Edge Cases

Callers must handle `NULL` or `ERR_PTR` `dev->rsc_dump` as unsupported, pass a page large enough for the command size, and destroy commands on all paths.

## Test Signals

Compile health reporter users and run resource dump paths on both unsupported and supported devices. Check that repeated `next()` calls terminate and cleanup frees PD/mkey resources.
