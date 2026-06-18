# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/Kconfig

## Purpose
This Kconfig entry exposes `CONFIG_MLX4_INFINIBAND`, the InfiniBand/RDMA driver for Mellanox ConnectX mlx4 adapters.

## Important APIs, Types, And Functions
`MLX4_INFINIBAND` is a tristate option labeled "Mellanox ConnectX HCA support". It depends on networking, Ethernet, PCI, and INET, and selects `NET_VENDOR_MELLANOX` plus `MLX4_CORE`.

## Control Flow
There is no runtime flow. The option controls whether `mlx4_ib` is built and ensures the core mlx4 PCI driver is selected.

## State And Persistence
Only build configuration state is represented.

## Dependencies And Integration Points
It integrates the mlx4 RDMA hardware driver with Kbuild and the mlx4 core driver. The help text identifies IPoIB and SRP as consumers.

## Risks
Dependency or select mistakes would break builds or allow mlx4_ib without mlx4 core. INET dependency is needed because the driver includes RoCE/IP address handling paths.

## Test Signals
Build with option disabled, built-in, and module; verify `MLX4_CORE` is selected and the Makefile links `mlx4_ib.o`.
