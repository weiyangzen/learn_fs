
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/phy.c

## Purpose
`phy.c` provides legacy MII/GMII PHY support for the IBM EMAC driver. It implements generic autonegotiation/forced-link operations, reset helpers for external PHYs and internal GPCS, several PHY-specific initialization sequences, and a probe routine that identifies a PHY by MII ID and fills `struct mii_phy`.

## Important APIs, Types, and Functions
Public functions are `emac_mii_reset_phy()`, `emac_mii_reset_gpcs()`, and `emac_mii_phy_probe()`. Generic operations are `genmii_setup_aneg()`, `genmii_setup_forced()`, `genmii_poll_link()`, and `genmii_read_link()`, grouped into `generic_phy_ops`. PHY-specific init routines include `cis8201_init()`, `m88e1111_init()`, `m88e1112_init()`, `et1011c_init()`, and `ar8035_init()`. The table `mii_phy_table` matches ET1011C, CIS8201, BCM5248, Marvell 88E1111/88E1112, Atheros AR8035, and a generic fallback.

## Control Flow
EMAC initializes a `mii_phy` with MDIO callbacks, then calls `emac_mii_phy_probe()` for candidate addresses. Probe resets the PHY, reads ID registers, selects a definition, derives supported link modes from BMSR/ESTATUS when the definition does not hard-code features, and initializes default advertising. Later link setup calls `setup_aneg()` or `setup_forced()`. Link polling reads BMSR twice to clear latches, waits for autoneg completion when enabled, and `read_link()` computes speed/duplex/pause from negotiated partner registers or BMCR forced settings. GPCS reset additionally programs SGMII-recommended registers.

## State and Persistence
The file mutates only `struct mii_phy` fields and PHY/GPCS MDIO registers. No state persists beyond hardware register settings and the EMAC-owned `mii_phy` instance.

## Dependencies and Integration Points
It depends on Linux MII/ethtool constants and the caller-provided MDIO read/write hooks in `struct mii_phy`. `core.c` integrates it into device-tree and legacy PHY discovery, and may replace it with phylib-backed operations when `phy-handle` is present.

## Risks
Vendor-specific register writes are hard-coded and board-sensitive. Generic feature discovery assumes standard MII registers behave correctly. The PHY table has a generic all-zero mask fallback, so unknown PHYs are accepted with generic operations rather than rejected. Reset polling returns a boolean-like timeout result, so callers must interpret nonzero as failure. GPCS address handling depends on EMAC mode and device-tree defaults.

## Test Signals
PHY detection logs, successful autonegotiation at 10/100/1000, forced speed/duplex changes through ethtool, pause/asymmetric pause reporting, link flap handling, and board-specific PHY initialization on CIS8201/Marvell/ET1011C/AR8035 hardware are useful signals. MDIO error injection should confirm probe skips absent addresses.
