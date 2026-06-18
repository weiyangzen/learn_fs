# sources/distributed-fs/ceph-client/include/linux/phy.h

## Purpose
Main Ethernet PHY library contract. It defines MAC-to-PHY interface modes, MDIO bus representation, PHY device state, PHY driver callbacks, link diagnostics, ethtool integration, timestamping hooks, PLCA/MSE/EEE support, LED integration, fixed and SFP attachment points, and helper APIs used by network MAC drivers and PHY drivers.

## Important APIs, Types, and Functions
Core types are `phy_interface_t`, `struct mii_bus`, `enum phy_state`, `struct phy_c45_device_ids`, `struct phy_device`, `struct phy_driver`, `struct phy_tdr_config`, `struct phy_plca_cfg`, `struct phy_plca_status`, `struct phy_mse_capability`, `struct phy_mse_snapshot`, and `struct phy_led`. Bus/device APIs include `mdiobus_alloc()`, `mdiobus_register()`, `mdiobus_unregister()`, `get_phy_device()`, `phy_device_create()`, `phy_device_register()`, `phy_attach_direct()`, `phy_connect()`, `phy_disconnect()`, `phy_start()`, and `phy_stop()`. Register helpers include `phy_read()`, `phy_write()`, `phy_read_mmd()`, `phy_modify*()`, and paged variants. Driver registration uses `phy_drivers_register()` and `module_phy_driver()`.

## Control Flow
The PHY lifecycle flows from MDIO bus allocation/registration, PHY scan/device creation, driver probe/config init, MAC attach/connect, autonegotiation configuration, state-machine polling or interrupts, link status resolution, ethtool operations, suspend/resume, and detach/unregister. Inline helpers choose generic fallbacks when driver callbacks are absent, such as `phy_read_status()` falling back to `genphy_read_status()`.

## State and Persistence
`struct phy_device` is the persistent per-PHY state container: identifiers, Clause 45 IDs, interface and possible-interface bitmaps, link speed/duplex/pause/autoneg, EEE advertisements, PLCA and diagnostics support, timestamp callbacks, LED lists, SFP/phylink attachment, delayed work state machine, mutex, interrupt state, statistics support, port list, and driver-private/shared data. `struct mii_bus` persists bus identity, callbacks, device map, IRQ map, reset GPIO, lock, and per-address stats.

## Dependencies and Integration Points
Integrates with MDIO, MII, ethtool, netdevice, phylink, SFP, LED triggers, MACsec, PTP timestamping, rtnetlink, workqueues, timers, module registration, and device model PM. Generic PHY helpers integrate with Clause 22, Clause 37, Clause 45, 10G, Base-T1, EEE, PLCA, OATC14, cable test, and link statistics code.

## Risks
High-risk areas are MDIO locking context, interrupt versus polling state, state-machine races, incorrect advertisement masks, interface mode mismatches, EEE/autonomous EEE negotiation, PHY/MAC timestamp selection, optional callback error handling, and userspace-visible diagnostics with vendor-specific scaling. Many helpers must not run in interrupt context because MDIO transactions can sleep.

## Test Signals
Signals include PHYLIB build matrices, MDIO bus scan tests, MAC driver attach/detach tests, phylink integration tests, ethtool ksettings/EEE/WoL/stats/cable-test coverage, interrupt and polling link-change tests, suspend/resume/WoL tests, and KUnit or driver selftests for generic Clause 22/45 helpers.
