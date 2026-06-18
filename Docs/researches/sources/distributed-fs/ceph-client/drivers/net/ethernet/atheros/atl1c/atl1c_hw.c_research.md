# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/atl1c_hw.c

## Purpose
`atl1c_hw.c` implements low-level hardware services for the ATL1C family: EEPROM/OTP detection and reads, MAC address acquisition/programming, multicast hash calculation, MDIO/PHY access, PHY reset and initialization, link status/speed reporting, autonegotiation restart, low-power link selection, WoL power-save programming, and post-link PHY tuning.

## Important APIs, types, and functions
EEPROM and MAC address functions include `atl1c_check_eeprom_exist()`, `atl1c_read_eeprom()`, `atl1c_read_mac_addr()`, and `atl1c_hw_set_mac_addr()`. `atl1c_get_permanent_address()` first trusts a BIOS-programmed station address, then triggers TWSI/OTP load, with extra voltage handling for L2C_B variants, and falls back to a random address through `atl1c_read_mac_addr()` if permanent address retrieval fails.

PHY access is centered on `atl1c_read_phy_core()` and `atl1c_write_phy_core()`, wrapped by normal, extension, and debug register helpers. They stop FPGA PHY polling when necessary, choose a slow MDIO clock while hibernating on selected chips, program `REG_MDIO_EXTN` for extended access, wait with `atl1c_wait_mdio_idle()`, and restart polling.

Link and power APIs include `atl1c_phy_reset()`, `atl1c_phy_init()`, `atl1c_get_link_status()`, `atl1c_get_speed_and_duplex()`, `atl1c_restart_autoneg()`, `atl1c_phy_to_ps_link()`, `atl1c_power_saving()`, and `atl1c_post_phy_linkchg()`.

## Control flow and state behavior
Initialization flows from reset/tuning to advertisement programming and `BMCR_RESET | BMCR_ANENABLE | BMCR_ANRESTART`. `hw->phy_configured` records whether PHY setup has been done. `hw->autoneg_advertised`, `hw->media_type`, and `hw->link_cap_flags` determine MII advertisement registers. Suspend power saving narrows link advertisement where possible, stores chosen speed/duplex in `adapter`, then programs MAC, master, GPHY, and WoL registers. State persists in hardware registers and in `hw` fields such as `hibernate`, `phy_configured`, and MAC addresses.

## Dependencies and integration points
The file depends on PCI device logging, Linux MII constants, CRC helpers, register constants from `atl1c_hw.h`, and the adapter state from `atl1c.h`. It is called by probe/resume/open/link-change paths in `atl1c_main.c` and by ethtool for EEPROM, link, and autoneg operations.

## Risks
Many operations are hardware-revision-specific. Wrong `nic_type` handling can break L2C_B voltage workarounds, L1D/L2CB EEE disablement, or ASPM/hibernate behavior. MDIO functions return `-1` rather than errno values, so callers must not expose them directly without translation. `atl1c_get_permanent_address()` has early returns on TWSI timeout that can bypass voltage/clock restoration after voltage was raised. The fallback to `eth_random_addr()` keeps the device usable but changes persistence and should set `NET_ADDR_RANDOM` in the caller.

## Test signals
Signals include valid permanent MAC detection, no MDIO timeout logs, successful autoneg at all supported speeds, correct speed/duplex reporting from `MII_GIGA_PSSR`, WoL magic/link wake from suspend, clean resume after hibernation, multicast filtering behavior, and stable link after cable changes on patched platforms.
