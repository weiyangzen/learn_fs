# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/Kconfig

## Purpose
This file defines mlx4 core and Ethernet driver configuration, including optional Data Center Bridging support, debug output, and old generation PCI ID support.

## Important Configuration
- `MLX4_EN` is the Ethernet driver tristate. It depends on PCI, networking, Ethernet, INET, and optional PTP clock support; it selects `PAGE_POOL` and `MLX4_CORE`.
- `MLX4_EN_DCB` enables DCB support when `MLX4_EN && DCB` are available.
- `MLX4_CORE` is the underlying mlx4 core tristate, selecting auxiliary bus and devlink support.
- `MLX4_DEBUG` and `MLX4_CORE_GEN2` toggle verbose diagnostics and old device ID support.

## Control Flow
Kconfig dependency resolution ensures the Ethernet driver pulls in core support and only exposes DCB when the generic DCB stack exists.

## State and Persistence
The chosen options persist in kernel configuration and affect which objects and features are compiled.

## Dependencies and Integration Points
This file integrates mlx4 with PCI, netdevice, PTP, DCB, page pool, auxiliary bus, and devlink subsystems.

## Risks and Test Signals
Risks include missing dependency selections for features used by the Makefile or source, and user-visible configuration combinations that compile but lack runtime support. Test signals are config matrix builds around `MLX4_EN`, `MLX4_EN_DCB`, `PTP_1588_CLOCK_OPTIONAL`, and `DCB`.
