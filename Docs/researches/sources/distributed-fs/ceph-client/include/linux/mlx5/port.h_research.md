# sources/distributed-fs/ceph-client/include/linux/mlx5/port.h

## Purpose
This header exposes mlx5 port capability, link mode, module EEPROM, autonegotiation, MTU, and InfiniBand port query interfaces. It is a declaration and constants layer used by mlx5 Ethernet, IB/RDMA, and management code.

## Important APIs, Types, And Data
- `enum mlx5_beacon_duration` defines off and infinite beacon duration values.
- `enum mlx5_module_id` identifies common transceiver module types such as SFP, QSFP, QSFP+, QSFP28, and DSFP.
- `enum mlx5_an_status` describes autonegotiation status values.
- I2C and EEPROM constants define low/high module I2C addresses and page sizes.
- `enum mlx5e_link_mode` and `enum mlx5e_ext_link_mode` map firmware link-mode bits to Ethernet media/rate names from 100M through 1600G classes.
- `enum mlx5e_connector_type` identifies physical connector categories.
- `enum mlx5_ptys_width` defines lane width masks.
- `MLX5E_PROT_MASK()` and `MLX5_GET_ETH_PROTO()` help construct mode masks and select standard versus extended PTYS fields.
- Exported functions query or modify port capabilities, PTYS, IB operational width/protocol, max/oper MTU, and VL hardware capability.

## Control Flow
Drivers query PTYS and module metadata to build ethtool link mode displays, validate requested speed/lane changes, and read active negotiated state. Port capability modification is explicit through `mlx5_set_port_caps()`. MTU and IB operational attributes are queried as needed by netdev and RDMA setup paths.

## State And Persistence
Port state is maintained by device firmware and physical link hardware: advertised/operational modes, module identity, MTU, VL capability, and autoneg status. The header maintains no state but defines the enum values that must match firmware registers.

## Dependencies And Integration Points
It includes `linux/mlx5/driver.h` for `struct mlx5_core_dev` and mlx5 access helpers. It integrates with mlx5e ethtool, devlink/port management, RDMA port queries, module EEPROM reads, and firmware PTYS register access.

## Risks
Link mode enum numeric values must match firmware bit positions. Adding modes requires updates in display/mapping tables outside this file. `MLX5_GET_ETH_PROTO()` must be called with the correct `ext` selector and register layout. Multi-plane or multi-port callers must pass correct `local_port` and `plane_index` to avoid reporting or configuring the wrong port.

## Test Signals
Compile-time users should cover all enum values in mapping tables. Runtime signals include ethtool advertised/supported mode output, module EEPROM reads at both I2C pages, successful MTU queries, IB operational width/protocol queries, and link-mode negotiation tests on standard and extended PTYS-capable devices.
