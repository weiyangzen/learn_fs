# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-mdio.c

## Purpose
PHY, ethtool, ioctl, carrier logging, and common stop/link helpers for Octeon Ethernet ports.

## Important APIs, Types, And Functions
Exports `cvm_oct_ethtool_ops`, `cvm_oct_ioctl()`, `cvm_oct_note_carrier()`, `cvm_oct_adjust_link()`, `cvm_oct_common_stop()`, and `cvm_oct_phy_setup_device()`.

## Control Flow
EtHTool reports driver info, exposes link state, and delegates link settings to phylib. IOCTL validates the device is running and has a PHY before calling `phy_mii_ioctl()`. PHY setup resolves `phy-handle` or fixed-link OF nodes, connects via `of_phy_connect()`, starts the PHY, or assumes carrier on for direct MAC links. Link adjustment converts phylib status into `cvmx_helper_link_info`, sets hardware link state, and logs changes. Stop disables GMX port, clears polling, disconnects PHY, and reports link down.

## State And Persistence
Updates `struct octeon_ethernet` fields `last_link`, `link_info`, and `poll`. No persistent storage exists.

## Dependencies And Integration Points
Depends on phylib, OF MDIO/fixed-link helpers, netdev ethtool/ioctl hooks, and CVMX link/GMX CSR helpers.

## Risks
No-PHY mode assumes link up. `phydev->duplex` and speed are trusted. Stop directly touches GMX registers and assumes `INTERFACE()`/`INDEX()` are valid for the port.

## Test Signals
PHY and fixed-link DT cases, missing PHY fallback, ethtool get/set link settings, MII ioctl, link-up/down transitions, stop while carrier is up, and probe deferral from missing PHY.
