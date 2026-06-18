# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/hw.h

## Purpose

This header defines the e1000e hardware abstraction: PCI device IDs, MAC/PHY/NVM/media enums, descriptor layouts, hardware statistic structures, operation-vector types, per-subsystem state structures, and the top-level `struct e1000_hw`. It is the contract between family-specific hardware files and generic netdev/ethtool/PTP code.

## Important APIs, Types, and Functions

Important enums include `e1000_mac_type`, `e1000_media_type`, `e1000_nvm_type`, `e1000_nvm_override`, `e1000_phy_type`, `e1000_bus_width`, `e1000_1000t_rx_status`, `e1000_rev_polarity`, `e1000_fc_mode`, `e1000_ms_type`, `e1000_smart_speed`, `e1000_serdes_link_state`, and `e1000_ulp_state`.

Important hardware data layouts include `union e1000_rx_desc_extended`, `union e1000_rx_desc_packet_split`, `struct e1000_tx_desc`, `struct e1000_context_desc`, `struct e1000_data_desc`, `struct e1000_hw_stats`, `struct e1000_phy_stats`, and host-management command/cookie structures.

The operation vectors are `struct e1000_mac_operations`, `struct e1000_phy_operations`, and `struct e1000_nvm_operations`. State structures include `struct e1000_mac_info`, `struct e1000_phy_info`, `struct e1000_nvm_info`, `struct e1000_bus_info`, `struct e1000_fc_info`, per-family `dev_spec` structures, and the aggregate `struct e1000_hw`.

## Control Flow

This header has no executable control flow, but it defines the dispatch model used throughout the driver. Probe code identifies a PCI device, selects a MAC type and `e1000_info` descriptor, copies operation tables into `struct e1000_hw`, and later generic paths invoke callbacks through `mac.ops`, `phy.ops`, and `nvm.ops`. The enums and state fields determine branches for media setup, reset behavior, NVM access method, PHY register access, power management, flow control, and SerDes link handling.

## State and Persistence Behavior

`struct e1000_hw` contains the live hardware-facing state: MMIO base pointers, MAC information, flow control settings, PHY state, NVM geometry, bus state, management cookie, and per-family device-specific state. Descriptor structures model DMA memory shared with hardware. `struct e1000_hw_stats` and `struct e1000_phy_stats` cache counters read from clear-on-read hardware registers. NVM and management structures represent persistent EEPROM/flash and firmware-facing command layouts.

## Dependencies and Integration Points

The header includes `regs.h` and `defines.h`, then includes family headers `82571.h`, `80003es2lan.h`, and `ich8lan.h` after `struct e1000_hw` is defined. It also includes `mac.h`, `phy.h`, `nvm.h`, and `manage.h` so operation signatures and helper declarations are available. `e1000.h` includes this file and exposes it to all main driver components.

## Risks and Edge Cases

This is a high-risk shared contract. Changing descriptor layout, endian annotations, operation-vector signatures, enum ordering, or state fields can break DMA interpretation, hardware-family dispatch, stats collection, or per-MAC workarounds. The union `dev_spec` requires each MAC family to use only its own member. Descriptor definitions must match hardware byte layout exactly.

## Test Signals

Build coverage catches many signature and layout reference errors, but hardware validation is required. Useful signals include successful probe for every listed PCI ID family, descriptor Tx/Rx traffic under checksum/TSO/VLAN/timestamp features, stats consistency, NVM access, PHY info reporting, SerDes state transitions, flow-control negotiation, and suspend/resume behavior across families.
