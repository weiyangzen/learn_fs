# sources/distributed-fs/ceph-client/drivers/net/phy/marvell10g.c

## Purpose
`marvell10g.c` implements the Marvell Alaska X/M multi-gigabit Clause 45 PHY driver for 88X3310/88X3340 and 88E2110/88E2111 devices. It handles firmware sanity checks, host MACTYPE selection, 10G/5G/2.5G/1G/100M/10M link reporting, copper/fiber priority behavior, EDPD and downshift tunables, WOL, hwmon, and `phy_port` integration for combo MII/MDI ports.

## Important APIs, Types, And Functions
- `struct mv3310_mactype` describes each hardware MACTYPE, whether the host interface is fixed, and the 10G interface mode it maps to.
- `struct mv3310_chip` is the per-chip operation table for downshift availability, supported interface initialization, MACTYPE get/set/select, MACTYPE arrays, and optional hwmon temperature register access.
- `struct mv3310_priv` stores supported host interfaces, selected MACTYPE, firmware version, downshift capability, and hwmon resources.
- Power and reset helpers include `mv3310_power_down()`, `mv3310_power_up()`, and `mv3310_reset()`.
- Configuration and feature hooks include `mv3310_probe()`, `mv3310_config_init()`, `mv3310_get_features()`, `mv3310_config_aneg()`, and `mv3310_config_mdix()`.
- Runtime status uses `mv3310_aneg_done()`, `mv3310_read_status()`, `mv3310_read_status_copper()`, `mv3310_read_status_10gbaser()`, and `mv3310_update_interface()`.
- User-facing controls include `mv3310_get_tunable()/set_tunable()`, `mv3110_get_wol()/set_wol()`, and hwmon callbacks.

## Control Flow And State Behavior
Probe verifies that the PHY is Clause 45 and exposes PMA/PMD plus AN MMDs, rejects firmware boot-fatal status, allocates `mv3310_priv`, reads the firmware version, computes downshift support, powers the port down to save energy, registers hwmon, initializes the supported host-interface bitmap, and advertises up to two modeled ports. `config_init` powers the device up, optionally changes MACTYPE based on `phydev->host_interfaces`, validates the resulting MACTYPE index, populates possible runtime interfaces, enables EDPD, and enables default downshift if supported. Autonegotiation config combines generic Clause 45 AN with vendor-specific 1000BASE-T advertisement and restarts AN if anything changed.

Runtime status first checks the BASE-R PCS link. If it is up, the driver reports a fixed 10G fiber link; otherwise it reads copper link state through generic C45 link checks plus vendor CSSR1 speed/duplex/MDIX bits, supplements 1G link partner advertisement through vendor AN registers, resolves pause, and adjusts `phydev->interface` according to fixed-rate-match or dynamic SGMII/2500BASE-X/5GBASE-R/10GBASE-R behavior. State is volatile in `mv3310_priv`; firmware version and MACTYPE live in hardware registers and survive across callbacks until reset or reconfiguration.

## Dependencies And Integration Points
The driver depends on phylib Clause 45 helpers, `linux/marvell_phy.h`, hwmon, ethtool PHY tunables, WOL, `phy_port`, and MMD register accessors. It integrates with MAC drivers through changing `phydev->interface`, with SFP/combo-port topology through `attach_mii_port()` and `attach_mdi_port()`, and with modalias matching through `mv3310_tbl[]`.

## Risks And Edge Cases
- MACTYPE selection must match the MAC's electrical interface; wrong selection can require hardware reset and break link.
- 88X3310/88X3340 share the same ID family and are distinguished by a port-count register, so reads during matching are part of identity detection.
- Some firmware versions lack reliable downshift; `mv3310_has_downshift()` gates the tunable.
- Power-up includes required delays and firmware-version-dependent software reset; removing those can make subsequent MDIO operations unreliable.
- Copper/fiber simultaneous connections have priority behavior where the first link can lock out the other path.
- WOL clear-status bit is not self-clearing and must be cleared after programming.

## Test Signals
Test with single-port and four-port 88X3310-family devices, 88E2110 versus 88E2111 speed capability detection, host-interface negotiation from `phydev->host_interfaces`, MACTYPE reset paths, copper speeds from 10M through 10G, 10GBASE-R fiber status, pause resolution, EDPD/downshift ethtool tunables, WOL enable/disable with magic packet address writes, suspend/resume power cycling, hwmon temperature reads, and `possible_interfaces` updates visible to MAC drivers.
