# sources/distributed-fs/ceph-client/drivers/net/phy/teranetics.c

## Purpose
`teranetics.c` is a Clause 45 phylib driver for the Teranetics TN2020 10G PHY. It reports fixed 10G full-duplex operation and handles a copper-versus-fiber distinction through a vendor register when checking autonegotiation and link status.

## Important APIs, Types, And Functions
Key functions are `teranetics_aneg_done()`, `teranetics_read_status()`, and `teranetics_match_phy_device()`. The driver table sets `PHY_10GBIT_FEATURES`, uses `gen10g_config_aneg`, custom aneg/status callbacks, and matches device ID slot 3 against `PHY_ID_TN2020`.

## Control Flow
`teranetics_aneg_done()` reads VEND1 register 93; when it is zero, the port is treated as copper and generic C45 autoneg completion is used, otherwise fiber mode returns done unconditionally. `teranetics_read_status()` starts with link up, 10G, full duplex. For copper mode it requires all PHYXS lane sync/alignment bits in `MDIO_PHYXS_LNSTAT` and AN `MDIO_STAT1_LSTATUS`; missing bits clear link.

## State And Persistence
The driver stores no private state. Status is derived from Clause 45 MMD registers and written into `phydev->link`, `speed`, and `duplex` on each read.

## Dependencies And Integration Points
It depends on phylib, Clause 45 MDIO constants, ethtool feature definitions, and module MDIO matching. It integrates as a specialized 10G PHY driver.

## Risks And Edge Cases
The VEND1 register 93 mode test treats a zero read as copper but does not handle negative errors in `teranetics_aneg_done()`. Fiber mode unconditionally reports autoneg done and link remains up unless copper checks run, so incorrect mode detection can produce false carrier. Link status checks are narrow to TN2020 lane-ready semantics.

## Test Signals
Test C45 matching by device ID, copper and fiber mode register 93 values, PHYXS lane sync/alignment failures, AN link-status failures, and MDIO read errors during status and autoneg checks.
