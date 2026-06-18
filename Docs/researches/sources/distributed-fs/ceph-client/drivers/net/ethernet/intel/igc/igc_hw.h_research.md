# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_hw.h

## Purpose
`igc_hw.h` defines the hardware-facing object model for the IGC driver. It identifies supported device IDs, operation tables, per-device MAC/NVM/PHY/flow-control state, PCI bus information, device-specific flags, and the hardware statistics layout.

## Important APIs, Types, And Functions
Key types include `struct igc_mac_operations`, `struct igc_nvm_operations`, `struct igc_phy_operations`, `struct igc_info`, `struct igc_mac_info`, `struct igc_nvm_info`, `struct igc_phy_info`, `struct igc_fc_info`, `struct igc_dev_spec_base`, `struct igc_hw`, and `struct igc_hw_stats`. Enums define MAC type, media type, NVM type, and flow-control mode. The file declares `igc_get_hw_dev()` and `hw_dbg()`, and exposes `igc_base_info`.

## Control Flow
The header has no direct runtime flow, but its operation tables drive dynamic dispatch for reset, initialization, link checks, physical setup, RAR programming, MAC address reads, speed/duplex reads, SW/FW semaphore acquisition, NVM access, and PHY access.

## State And Persistence
`struct igc_hw` is the central persistent runtime state embedded in `struct igc_adapter`. It stores MMIO base, backpointer, MAC addresses, multicast table shadow, RAR counts, firmware flags, NVM geometry and ops, PHY addressing and advertisement, flow-control watermarks/modes, bus function, device IDs, and revision. `struct igc_hw_stats` is the software accumulation target for hardware counters.

## Dependencies And Integration Points
It includes Linux types, Ethernet/netdevice definitions, register definitions, hardware defines, MAC/PHY/NVM/I225/base headers. `igc_base.c` fills operation tables, `igc_main.c` embeds and initializes `struct igc_hw`, and ethtool/diagnostic/MAC/NVM code read and mutate its fields.

## Risks
Changing structure layout or operation contracts affects nearly every driver path. NULL operation pointers are possible for unsupported NVM write/update/validate paths, so callers must respect initialization outcomes. Cached fields such as flow-control mode, advertised link modes, and EEE enablement must stay synchronized with hardware programming.

## Test Signals
Signals include successful probe across supported PCI IDs, reset/init behavior, MAC address programming, NVM reads, PHY register access, link negotiation, flow-control configuration, statistics updates, and build coverage for all operation table users.
