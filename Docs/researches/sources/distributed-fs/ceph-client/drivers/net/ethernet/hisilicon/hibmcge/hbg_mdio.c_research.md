
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_mdio.c

## Purpose

This file implements HIBMCGE MDIO Clause 22 access, PHY/fixed-PHY setup, PHY link adjustment, pause autonegotiation handling, PHY start/stop wrappers, and retry logic for MAC-to-PHY NP link failures.

## Important APIs, Types, and Functions

- `hbg_mdio_read22()` and `hbg_mdio_write22()` are the `mii_bus` callbacks.
- `hbg_mdio_cmd_send()` formats and starts an MDIO transaction and waits for completion.
- `hbg_mdio_init()` creates/registers the MDIO bus or registers a fixed PHY when `HBG_NO_PHY` is reported.
- `hbg_phy_adjust_link()` maps PHY speed/duplex to HIBMCGE SGMII port mode, calls `hbg_hw_adjust_link()`, and applies flow control.
- `hbg_fix_np_link_fail()` retries PHY stop/start up to five times when MAC NP link stays down.
- `hbg_phy_start()` and `hbg_phy_stop()` wrap PHYLIB operations for netdev open/stop and recovery.

## Control Flow

MDIO initialization reads the device-provided PHY address. If no external PHY exists, it registers a fixed 1 Gbps full-duplex PHY with pause/asym-pause. Otherwise it allocates a devm MDIO bus, masks all PHY addresses except the target, registers the bus, obtains the PHY, initializes the MDIO hardware clock fields, and connects the PHY with SGMII mode. Link adjustment runs from PHYLIB callbacks and only reprograms hardware when link state changes.

## State and Persistence

The file populates `priv->mac.phy_addr`, `mdio_bus`, `phydev`, speed, duplex, autoneg, link status, and pause autoneg fields. Hardware MDIO command registers hold transient operations. Fixed PHY and PHY connections are device-managed.

## Dependencies and Integration Points

It depends on PHYLIB, fixed PHY, MDIO bus registration, RTNL for NP link repair, hardware register helpers, and link/pause helpers from `hbg_hw.c`. It is started/stopped by `hbg_main.c` and used by ethtool PHY operations.

## Risks and Edge Cases

Only Clause 22 operations are implemented. MDIO timeout is one second with 5 ms polling. `hbg_fix_np_link_fail()` dereferences `phydev` and only retries when PHY link is up; repeated failure logs after five attempts and resets the counter. Fixed PHY path bypasses MDIO entirely. Link adjustment ignores unsupported PHY speeds.

## Test Signals

Signals include MDIO bus registration, PHY discovery at the device-provided address, fixed-PHY operation for `HBG_NO_PHY`, link-up/down status prints, correct 10/100/1000 SGMII mode programming, pause autoneg behavior, MDIO timeout handling, and NP-link repair attempts.
