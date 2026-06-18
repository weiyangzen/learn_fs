# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/Kconfig

## Purpose
This Kconfig entry defines `MLX5_INFINIBAND`, the tristate option enabling the mlx5 RDMA/InfiniBand driver for Mellanox fifth-generation ConnectX-family adapters.

## Important APIs, types, and functions
There are no C APIs in this file. The important symbol is `CONFIG_MLX5_INFINIBAND`. Its dependency expression is `NETDEVICES && ETHERNET && PCI && MLX5_CORE`, and the user-visible prompt is "Mellanox 5th generation network adapters (ConnectX series) support".

## Control flow
At kernel configuration time this symbol determines whether the mlx5 IB module is not built, built in, or built as a module. The help text states that it provides low-level InfiniBand support required for protocols such as IP-over-IB and SRP on Mellanox Connect-IB PCIe HCAs.

## State and persistence behavior
The selected value persists only in the kernel build configuration, normally `.config`, and controls compilation/linkage. It has no runtime state.

## Dependencies and integration points
The option depends on the networking, Ethernet, PCI, and mlx5 core driver stacks. The corresponding Makefile consumes the symbol via `obj-$(CONFIG_MLX5_INFINIBAND)`.

## Risks
Risk is mostly configuration-level: missing dependencies hide the driver, and enabling mlx5 IB without mlx5 core is impossible by design. Help text is narrow compared with the broader mlx5 RDMA feature set but does not affect behavior.

## Test signals
Check all three tristate modes, ensure `mlx5_ib.o` appears only when expected, verify dependency visibility in menuconfig/allmodconfig, and boot/module-load test with `CONFIG_MLX5_CORE` enabled.
