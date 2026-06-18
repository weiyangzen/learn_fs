# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_mdio.c

## Purpose
`ngbe_mdio.c` implements MDIO bus access and phylink MAC callbacks for the GbE PF driver. It supports internal MDI-style PHY register access and external RGMII/Clause 22/Clause 45 access through shared MDIO helpers, then uses phylink to manage link state.

## Important APIs, Types, and Functions
Public entry point is `ngbe_mdio_init()`. Internal helpers are `ngbe_phy_read_reg_internal()`, `ngbe_phy_write_reg_internal()`, `ngbe_phy_read_reg_c22()`, `ngbe_phy_write_reg_c22()`, `ngbe_mac_config()`, `ngbe_mac_link_down()`, `ngbe_mac_link_up()`, and `ngbe_phylink_init()`. `ngbe_mac_ops` supplies phylink callbacks.

## Control Flow
Probe calls `ngbe_mdio_init()`, which allocates a devm MDIO bus, sets read/write callbacks and phy mask, enables Clause 45 callbacks for RGMII, registers the bus, finds the first PHY, initializes link fields, and creates a phylink instance. On link up, phylink configures flow control, writes LAN speed, sets MAC TX speed/enable, refreshes RX config and watchdog registers, updates `wx->speed`, resets PTP cycle counter if active, and notifies VFs. Link down sets unknown speed, resets PTP cycle counter, and notifies VFs.

## State and Persistence Behavior
State lives in devm MDIO bus resources, `wx->phydev`, `wx->phylink`, link/speed/duplex fields, phylink config, flow-control registers, MAC speed registers, and PTP timing state. No disk persistence exists.

## Dependencies and Integration Points
It depends on Linux MDIO/PHY/phylink APIs, shared `wx` MDIO helpers (`wx_phy_read/write_reg_mdi_c22/c45`), PTP helpers, SR-IOV link notifications, and `ngbe_type.h` speed/register constants.

## Risks and Edge Cases
Internal MDIO reads return `0xffff` for nonzero PHY addresses instead of an error, which can mask address bugs. `ngbe_mac_config()` is empty, so all MAC changes occur in link-up/down. The PHY mask excludes addresses 4-31, assuming PHY address below 4. Phylink fixed TX delay comment must match board design.

## Test Signals
Test MDIO discovery on MDI and RGMII hardware, Clause 22/45 reads/writes, no-PHY failure, link up/down at 10/100/1000, pause negotiation, PTP reset on link transitions, and VF link notifications.
