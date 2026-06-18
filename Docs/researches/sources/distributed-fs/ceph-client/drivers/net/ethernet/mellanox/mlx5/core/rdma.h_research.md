# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/rdma.h

## Purpose

`rdma.h` exposes the mlx5 RoCE enable/disable hooks to the core driver while hiding the implementation behind `CONFIG_MLX5_ESWITCH`.

## Important APIs and Control Flow

When eswitch support is enabled, it declares `mlx5_rdma_enable_roce()` and `mlx5_rdma_disable_roce()` from `rdma.c`. Otherwise it provides inline stubs: enable returns success and disable is empty. This lets callers sequence RDMA setup unconditionally without scattering Kconfig checks.

## State and Dependencies

The header includes `mlx5_core.h` and has no storage. In enabled builds, calls mutate vport RoCE, GID, and flow steering state. In disabled builds, no state is changed.

## Risks and Test Signals

The main risk is assuming RoCE was actually enabled in non-eswitch builds because the stub returns 0. Compile both Kconfig paths and exercise callers that depend on RoCE availability checks separately from this helper's success code.
