# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/def.h

## Purpose
This header defines RTL8192CE/RTL8188CE chip-version, queue, RF, power, interface, descriptor-selection, PHY-status, and H2C command metadata used by the CE PCI driver.

## Important APIs, Types, And Functions
Key macros include RSSI/link-quality window sizes, channel-offset constants, RX queue IDs, chip-version bit masks, bonding identifiers, and RF type markers. Important enums are `version_8192c`, `rtl819x_loopback_e`, `rf_optype`, `rf_power_state`, `power_save_mode`, `power_polocy_config`, `interface_select_pci`, and `rtl_desc_qsel`. Small data structures include `phy_sts_cck_8192s_t` and `h2c_cmd_8192c`.

## Control Flow
The header is declarative. `hw.c` reads hardware registers into `enum version_8192c` values, maps those to RF topology, and uses queue IDs and descriptor selectors when programming DMA and descriptors. PHY code uses `rf_optype` to select direct or firmware RF register access.

## State And Persistence
No storage is declared. The enums and macros classify runtime state kept in `rtlhal`, `rtlphy`, PCI rings, and firmware command buffers.

## Dependencies And Integration Points
It is included by CE hardware, PHY, RF, DM, and common PHY code. It links register-level chip detection with rtlwifi-wide concepts such as RF paths, power states, and descriptor queues.

## Risks And Edge Cases
The chip-version enum encodes vendor, cut, package, and RF topology in bit fields, so incorrect masks can misclassify devices and choose wrong 1T/2T tables. The typo `power_polocy_config` is API surface. `struct phy_sts_cck_8192s_t` maps receive PHY reports and is layout-sensitive.

## Test Signals
Probe logs reporting the expected chip version and RF type, correct RX queue selection, valid descriptor qsel mapping, and stable RF operation across 88C, 92C, 1T1R, 1T2R, and 2T2R variants are the main validation signals.
