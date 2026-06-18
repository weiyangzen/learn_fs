<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/of_net.c -->
# sources/distributed-fs/ceph-client/net/core/of_net.c

## Purpose
Open Firmware/device-tree helpers for network drivers to parse PHY interface mode and MAC address data, including fallback to NVMEM cells.

## APIs, Types, and Functions
Exports `of_get_phy_mode()`, `of_get_mac_address_nvmem()`, `of_get_mac_address()`, and `of_get_ethdev_address()`. Private `of_get_mac_addr()` validates a named property as exactly `ETH_ALEN` bytes and a valid nonzero Ethernet address.

## Control Flow, State, and Persistence
`of_get_phy_mode()` reads `phy-mode` or `phy-connection-type`, compares case-insensitively against `phy_modes()`, and returns `PHY_INTERFACE_MODE_NA` plus an errno on failure. MAC lookup tries `mac-address`, then `local-mac-address`, then legacy `address`, then NVMEM. NVMEM lookup first uses a platform device associated with the node, then falls back to an OF NVMEM cell named `mac-address`, validates length/address, copies it, and frees the cell buffer. `of_get_ethdev_address()` writes the discovered address into `dev->dev_addr`.

## Dependencies and Integration
Depends on OF property APIs, platform-device lookup, NVMEM consumer APIs, Ethernet address validation, PHY mode tables, and netdevice address helpers. It is used by DT-aware Ethernet drivers during probe.

## Risks and Test Signals
Risks include accepting obsolete `address` when a board uses it for another meaning, NVMEM provider deferral/error propagation, and invalid zero MACs from boot firmware. Test signals are property precedence, invalid/all-zero MAC rejection, NVMEM fallback with correct buffer free, `-ENODEV` for unknown PHY strings, and successful `eth_hw_addr_set()` through `of_get_ethdev_address()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/of_net.c -->
