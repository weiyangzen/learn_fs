# sources/distributed-fs/ceph-client/drivers/net/mii.c

## Purpose
This file is the legacy MII helper library used by Ethernet drivers that manage PHYs through `struct mii_if_info`. It translates MII/GMII registers into ethtool settings, applies requested link advertisements or forced media settings, checks link and media state, restarts autonegotiation, and handles old MII ioctl commands.

## Important APIs, Types, and Functions
The key dependency type is `struct mii_if_info`, supplied by caller drivers with `mdio_read`, `mdio_write`, `dev`, `phy_id`, masks, and capability flags. Exported functions include `mii_ethtool_gset()`, `mii_ethtool_get_link_ksettings()`, `mii_ethtool_sset()`, `mii_ethtool_set_link_ksettings()`, `mii_check_gmii_support()`, `mii_link_ok()`, `mii_nway_restart()`, `mii_check_link()`, `mii_check_media()`, and `generic_mii_ioctl()`. Internal `mii_get_an()` reads advertised or partner abilities and converts them to ethtool legacy bitmaps.

## Control Flow
The get-settings paths read `MII_BMCR`, `MII_BMSR`, and, when GMII is supported, `MII_CTRL1000` and `MII_STAT1000`. They build supported/advertising/link-partner fields, determine negotiated or forced speed/duplex, update `mii->full_duplex`, and convert to either legacy `ethtool_cmd` or modern link-mode arrays. The set-settings paths validate speed, duplex, port, phy address, autoneg mode, and GMII capability. For autoneg, they rewrite advertisement registers, optionally `MII_CTRL1000`, then set `BMCR_ANENABLE | BMCR_ANRESTART`; for forced mode, they clear autoneg/speed/duplex bits and set the requested BMCR bits. Link check reads BMSR twice to handle latch behavior. Media check compares old/new carrier, updates netdev carrier, reads advertised/LPA registers, reports link messages, and returns whether duplex changed. The ioctl handler masks phy/reg ids, handles read commands, tracks duplex/advertising side effects for writes, and delegates MDIO writes.

## State and Persistence
The library does not allocate or own objects. It updates fields in the caller-owned `mii_if_info`: `full_duplex`, `force_media`, and `advertising`. It also changes persistent PHY register state through caller-provided MDIO operations and updates netdev carrier state. There is no internal locking; callers must serialize if their MDIO path or netdev state requires it.

## Dependencies and Integration Points
The file integrates with MDIO register definitions, ethtool legacy and link-ksettings APIs, netdevice carrier APIs, and ioctl commands `SIOCGMIIPHY`, `SIOCGMIIREG`, and `SIOCSMIIREG`. It is exported as GPL module symbols for older drivers rather than being a standalone device driver.

## Risks and Edge Cases
Autoneg result calculation can fall back to 10 Mbps when no common ability is available, which matches legacy behavior but can be misleading if reads failed. The code does not check negative MDIO read errors before interpreting register bits, so drivers must provide reliable callbacks or tolerate odd ethtool output. Forced 1000 Mbps is allowed only when `supports_gmii`; half/full setting is derived directly from BMCR. `generic_mii_ioctl()` allows writes to arbitrary masked PHY/register pairs and only updates cached state when the target PHY matches `mii_if->phy_id`.

## Test Signals
Tests should cover C22 register read/write callback interactions, ethtool get/set for legacy and link-ksettings APIs, autoneg restart, forced speed/duplex, GMII support detection through `BMSR_ESTATEN` and `MII_ESTATUS`, link latch double-read behavior, carrier transitions, and ioctl read/write state changes. Driver tests should verify caller locking and correct duplex-change notifications.
