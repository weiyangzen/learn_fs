# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/dcbnl.h

## Purpose

`en/dcbnl.h` defines mlx5e DCB/DCBX state and lifecycle hooks, with no-op stubs when DCB support is disabled.

## Important APIs, Types, and Functions

- `MLX5E_MAX_PRIORITY` and `MLX5E_MAX_DSCP` define priority/DSCP sizing.
- `struct mlx5e_cee_config` stores pending CEE priority group bandwidth, priority-to-PG mapping, PFC settings, and PFC enablement.
- `struct mlx5e_dcbx` stores DCBX mode, CEE config, DSCP app count, TSA state, capability, buffer configuration, and rate upper limits.
- `struct mlx5e_dcbx_dp` stores datapath DSCP-to-priority mapping and trust state.
- DCB hooks: `mlx5e_dcbnl_build_netdev()`, `mlx5e_dcbnl_initialize()`, `mlx5e_dcbnl_init_app()`, `mlx5e_dcbnl_delete_app()`.

## Control Flow

When `CONFIG_MLX5_CORE_EN_DCB` is enabled, netdev setup and private initialization call these hooks to register DCBNL ops and initialize app/firmware state. Otherwise calls compile to no-ops.

## State and Persistence Behavior

The structures are embedded in `struct mlx5e_priv` when DCB is enabled and persist with the netdev. Datapath state maps DSCP to priorities and trust mode.

## Dependencies and Integration Points

Depends on DCB/DCBX kernel types via users of the enabled configuration and integrates with `en.h`, netdev DCBNL operations, PFC, CEE/IEEE app configuration, and port buffer code.

## Risks and Edge Cases

- Disabled builds silently omit DCB behavior through stubs.
- Comments note `tc_tsa` is not readable from firmware, so driver state is authoritative for that field.
- DSCP array sizing must match valid DSCP values.

## Test Signals

Compile with and without DCB support. Use `dcb`/`lldptool` operations for PFC, ETS, DSCP trust, and app add/delete. Verify netdev ops are absent/no-op in disabled builds.
