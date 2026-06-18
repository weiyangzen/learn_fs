# sources/distributed-fs/ceph-client/drivers/net/phy/nxp-tja11xx.c

## Purpose
This is the Clause 22 NXP TJA1100/TJA1101/TJA1102/TJA1102S BroadR-Reach/100BASE-T1 PHY driver. It manages power/wakeup, forced 100 Mbps full-duplex link operation, master/slave role, MII/RMII/RGMII-style interface selection, cable tests, SQI, hwmon temperature, statistics, interrupts, and special dual-port TJA1102 discovery.

## Important APIs, Types, and Functions
The driver uses `struct tja11xx_priv` to hold a `phy_device` pointer, hwmon state, and flags such as RMII refclk input. Core helpers include `tja11xx_check()`, `phy_modify_check()`, register-write enable/link-control helpers, `tja11xx_wakeup()`, `tja11xx_soft_reset()`, `tja11xx_config_aneg()`, `tja11xx_config_init()`, `tja11xx_read_status()`, SQI/stats functions, hwmon callbacks, DT parsing, probe functions, TJA1102 port matching/discovery, interrupt callbacks, and cable-test callbacks.

## Control Flow
Probe allocates private state, parses device-tree settings such as `nxp,rmii-refclk-in`, registers hwmon when supported, and for TJA1102 port 0 may create/register the second PHY device on the next MDIO address. Init enables configuration writes, forces autoneg disabled with 100/full defaults, programs interface mode per PHY variant and selected host interface, clears sleep confirmation, programs sleep request timeout, wakes the PHY, and acknowledges interrupts.

Config-aneg maps `phydev->master_slave_set` into the TJA master/slave bit, optionally starts cable test autoneg behavior when link is down and a cable-test operation is available, and then delegates generic config-aneg. Read-status updates link, master/slave state, communication status, and fixed 100/full state. Interrupt paths acknowledge and enable device-specific interrupt masks, then trigger the state machine on asserted events.

## State and Persistence
Private state persists in `phydev->priv`, while most behavior is hardware-register based. The driver uses `phydev` fields for forced autoneg, speed, duplex, master/slave configuration, interface mode, SQI, and stats. TJA1102 dual-port discovery creates a second `phy_device`, so bus/device lifetime is a key persistence concern.

## Dependencies and Integration Points
The file integrates with phylib, ethtool cable-test netlink, hwmon, device tree, MII register helpers, module PHY registration, and generic helpers such as `genphy_*`. It is a predecessor/parallel driver to the Clause 45 TJA11xx support in this subset.

## Risks
Wakeup and config-write sequences are hardware timing sensitive. Dual-port TJA1102 creation must avoid address conflicts and incorrect port matching. Cable-test autoneg side effects can surprise link bring-up if invoked at the wrong time. Interface mode flags differ by PHY variant and DT property. Temperature and stats reads must handle absent hardware support cleanly.

## Test Signals
Test each supported PHY ID, TJA1102 port0/port1 discovery, wake from sleep, all supported host interface modes, RMII refclk DT behavior, forced master/slave modes, link status and SQI, cable tests, hwmon reads, interrupts, stats, and suspend/resume.
