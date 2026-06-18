# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/Makefile

## Purpose
This Makefile defines the mlx4 core and mlx4 Ethernet module object composition.

## Important Build Rules
- `mlx4_core-y` aggregates allocator, command, CQ/EQ, firmware, ICM, interface, main, multicast, memory registration, port, profile, QP, reset, sense, SRQ, resource tracker, and crash dump code.
- `mlx4_en-y` aggregates Ethernet main, TX/RX, ethtool, port, CQ, resource, netdev, selftest, and clock files.
- `mlx4_en-$(CONFIG_MLX4_EN_DCB) += en_dcb_nl.o` conditionally adds DCB netlink support.

## Control Flow
Kbuild builds `mlx4_core.o` when `CONFIG_MLX4_CORE` is set and `mlx4_en.o` when `CONFIG_MLX4_EN` is set. DCB support is compiled only under its Kconfig option.

## State and Persistence
There is no runtime state. The file persists module composition and therefore controls which symbols are linked.

## Dependencies and Integration Points
It integrates with mlx4 Kconfig symbols and the kernel module build system.

## Risks and Test Signals
Risks include missing objects when source files add external symbols, or DCB symbols referenced without the conditional object. Test signals are module builds with and without `CONFIG_MLX4_EN_DCB`.
