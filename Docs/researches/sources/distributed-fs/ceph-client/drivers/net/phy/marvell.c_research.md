# sources/distributed-fs/ceph-client/drivers/net/phy/marvell.c

## Purpose
`marvell.c` implements the Linux phylib driver family for a broad set of Clause 22 Marvell Ethernet PHYs: classic 10/100/1000 copper parts, combo copper/fiber parts, switch-embedded PHY families, and selected Marvell/Aquantia-like switch PHYs. It provides PHY identification, page-based register access, autonegotiation, interrupt handling, copper/fiber status resolution, suspend/resume, ethtool tunables, hardware statistics, wake-on-LAN, cable diagnostics, hwmon temperature sensors, LED control, and a `phy_port` SERDES attachment path for 88E1510-class devices.

## Important APIs, Types, And Functions
- `struct marvell_priv` is the per-PHY private state. It accumulates ethtool statistics, stores hwmon registration data, and tracks cable-test/TDR state such as range, step, pair, and 88E3082 VCT phase.
- Page helpers `marvell_read_page()`, `marvell_write_page()`, and `marvell_set_page()` expose the Marvell page register at `MII_MARVELL_PHY_PAGE`.
- Interrupt entry points are `marvell_config_intr()`, `marvell_ack_interrupt()`, and `marvell_handle_interrupt()`, using `MII_M1011_IEVENT` and `MII_M1011_IMASK`.
- Autonegotiation/configuration paths include `marvell_config_aneg()`, `m88e1101_config_aneg()`, `m88e1121_config_aneg()`, `m88e1111_config_aneg()`, `m88e1510_config_aneg()`, and chip-specific `*_config_init()` functions.
- Status and power paths include `marvell_read_status()`, `marvell_read_status_page()`, `marvell_suspend()`, `marvell_resume()`, and `m88e1510_resume()`.
- Ettool support covers downshift and fast-link-down tunables, `marvell_get_stats()`, `m88e1318_get_wol()/set_wol()`, `m88e1510_loopback()`, VCT5/VCT7 cable-test hooks, hwmon methods, and LED brightness/blink/hardware-trigger methods.
- `marvell_drivers[]` binds all supported PHY IDs to the applicable phylib callbacks and `marvell_tbl[]` exports MDIO modalias matching.

## Control Flow And State Behavior
Probe allocates `struct marvell_priv` with devres and optionally registers an hwmon device. `config_init` programs chip errata, interface mode, RGMII delays, LED defaults, DT `marvell,reg-init` overrides, downshift defaults, and software resets as required by each part. `config_aneg` then sets MDI/MDIX polarity, writes copper/fiber advertisements where applicable, and resets or restarts autonegotiation when a commit is needed. Runtime status first checks fiber on combo PHYs unless SGMII mode prevents that, then falls back to copper and updates `phydev->speed`, `duplex`, `port`, pause flags, and MDI-X state. Suspend/resume mirrors this page order and the 88E1510 resume path toggles downshift to clear an erratum counter.

The only persistent software state is in-memory `phydev->priv` and registered device resources. Hardware state is persisted in MDIO registers across callbacks, including page selection, LED/WOL registers, downshift fields, and cable-test state machines. Page-changing functions carefully restore pages on error in multi-register sequences, but some mode/status paths intentionally remain on the fiber page when fiber link is active.

## Dependencies And Integration Points
The driver depends on phylib, ethtool netlink cable-test reporting, hwmon, LED trigger support, OF MDIO properties, `linux/marvell_phy.h` IDs/flags, `phy_port`, and standard MII/MDIO helpers. It integrates with MAC drivers through phylib callbacks, with device tree through `marvell,reg-init`, with wakeup via `attached_dev->dev_addr`, and with SFP/port modeling through `m88e1510_attach_mii_port()`.

## Risks And Edge Cases
- Page selection is the dominant correctness risk; a missing restore can make later generic PHY reads hit the wrong register bank.
- Many initialization paths encode chip errata and undocumented magic writes. Simplifying them can regress specific PHY revisions.
- Combo copper/fiber parts have intentional fiber-priority behavior and special SGMII exceptions.
- WOL setup assumes `phydev->attached_dev` and its MAC address are valid when enabling magic-packet matching.
- Cable tests disable autonegotiation and may block link for the test duration; TDR graph collection locks the bus for many MDIO operations.
- Statistics counters are accumulated in software from hardware counters and return `U64_MAX` on read errors.

## Test Signals
Useful signals include module build with and without `CONFIG_OF_MDIO`/`CONFIG_HWMON`, probe for every table entry, page restore after failed MDIO operations, interrupt mask/ack behavior, copper and fiber link transitions, RGMII delay programming, ethtool downshift/fast-link-down get/set, WOL magic/link wake, LED hardware triggers, loopback at 10/100/1000, cable-test normal and TDR modes, hwmon temperature reads, suspend/resume on 88E1510, and SFP/SERDES port reconfiguration.
