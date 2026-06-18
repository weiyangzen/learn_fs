# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/Kconfig

## Purpose

This Kconfig file defines build-time feature selection for the mlx5 core driver and its Ethernet, SR-IOV, offload, steering, subfunction, FPGA, DPLL, and crypto acceleration features. It controls which pieces of the large `mlx5_core` module are available and which kernel subsystems must be present.

## Important Options

- `MLX5_CORE`: tristate core driver for Mellanox/NVIDIA 5th generation ConnectX/Connect-IB adapters; depends on PCI, optional MLXFW, optional PTP, optional Hyper-V PCI interface, optional HWMON, and selects `AUXILIARY_BUS` and `NET_DEVLINK`.
- `MLX5_CORE_EN`: Ethernet support; depends on networking and `MLX5_CORE`, selects page pool and DIM support.
- `MLX5_EN_ARFS`, `MLX5_EN_RXNFC`, and `MLX5_MPFS`: Ethernet receive steering/classification and multi-PF switch features.
- `MLX5_ESWITCH`: SR-IOV e-switch support, including legacy and switchdev modes.
- `MLX5_BRIDGE`, `MLX5_CLS_ACT`, `MLX5_TC_CT`, and `MLX5_TC_SAMPLE`: bridge and traffic-control offload support.
- `MLX5_CORE_EN_DCB`, `MLX5_CORE_IPOIB`: DCB and IPoIB feature gates.
- `MLX5_MACSEC`, `MLX5_EN_IPSEC`, `MLX5_EN_TLS`, `MLX5_EN_PSP`: cryptographic/security protocol offload gates.
- `MLX5_SW_STEERING` and `MLX5_HW_STEERING`: software-managed and hardware-managed flow steering.
- `MLX5_SF` and `MLX5_SF_MANAGER`: auxiliary-bus subfunction device support and devlink-managed subfunction ports.
- `MLX5_DPLL`: separate tristate DPLL support.
- `MLX5_FPGA`: Innova FPGA support compiled into mlx5 core.

## Control Flow

Kconfig has no runtime control flow. It contributes compile-time symbols that drive object inclusion in the adjacent Makefile and preprocessor/runtime feature availability elsewhere in the driver.

## State And Persistence Behavior

The file contributes kernel configuration state. Selected symbols persist in the kernel build configuration and module composition, not in runtime driver state.

## Dependencies And Integration Points

The options integrate mlx5 with PCI, devlink, auxiliary bus, netdev, RFS, switchdev, bridge, TC, netfilter flow table, MACsec, XFRM/IPsec, kTLS, software/hardware steering, subfunction auxiliary devices, DPLL, page pool, DIM, DCB, HWMON, Hyper-V, and PTP subsystems. The dependency expressions also protect invalid built-in/module combinations such as TLS built as a module while mlx5 core is built in.

## Risks

- Feature gates are highly cross-dependent; weakening dependencies can create link errors or runtime feature exposure without required subsystems.
- Defaults of `y` for several offload features can increase module surface area unexpectedly when dependencies are enabled.
- Hidden bools such as `MLX5_BRIDGE` and `MLX5_SF_MANAGER` are selected through dependency/default logic and may be overlooked in build matrix testing.

## Test Signals

Important signals are allmodconfig/allyesconfig/allnoconfig builds, representative modular builds, and targeted configs for switchdev, TC CT/sample, IPsec/TLS/MACsec/PSP, SF, FPGA, DPLL, HWMON, Hyper-V, and PTP combinations. Kconfig warnings and unresolved symbol/link failures are the primary validation outputs.
