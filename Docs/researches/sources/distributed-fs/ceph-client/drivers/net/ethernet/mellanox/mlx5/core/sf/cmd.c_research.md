# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/cmd.c

## Purpose

`sf/cmd.c` is the low-level command wrapper file for mlx5 subfunctions. It allocates/deallocates SF firmware function IDs and enables/disables the HCA for a specific SF function.

## Important APIs and Control Flow

`mlx5_cmd_alloc_sf()` sends `ALLOC_SF` with a function id. `mlx5_cmd_dealloc_sf()` sends `DEALLOC_SF`. `mlx5_cmd_sf_enable_hca()` sends `ENABLE_HCA` with `embedded_cpu_function` cleared and the SF function id. `mlx5_cmd_sf_disable_hca()` sends `DISABLE_HCA` similarly. All functions use fixed-size command buffers and return command executor status directly.

## State and Persistence Behavior

Successful commands mutate firmware SF allocation and HCA state. This file stores no local state, so higher-level SF tables own function id selection, software-to-hardware mapping, deferred free, and state transitions.

## Dependencies and Integration Points

It depends on `priv.h` declarations and the mlx5 command interface. `sf/hw_table.c` uses alloc/dealloc and `sf/devlink.c` uses enable/disable during devlink port function state changes.

## Risks and Test Signals

The wrappers are thin, so most risk is misuse by callers. One detail to verify is that `mlx5_cmd_sf_disable_hca()` sets `embedded_cpu_function` using the `enable_hca_in` macro name on the disable input buffer; if layouts diverge, this could become wrong. Tests should cover SF create/delete, active/inactive transitions, command-failure rollback, and EC-function platforms.
