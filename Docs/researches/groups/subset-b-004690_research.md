# subset-b-004690 research

Grouped research report for PHY and MDIO files under `sources/distributed-fs/ceph-client/drivers/net/phy/`. Each section preserves the source path and is delimited for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/marvell.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/marvell.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/marvell10g.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/marvell10g.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mdio-open-alliance.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mdio-open-alliance.h

## Purpose
`mdio-open-alliance.h` is a register-definition header for OPEN Alliance TC14 10BASE-T1S PHY features. It contains no executable logic; it gives PHY drivers common constants for PLCA control/status and advanced diagnostic features located in the Vendor 2 MMD.

## Important APIs, Types, And Constants
- PLCA register addresses include `MDIO_OATC14_PLCA_IDVER`, `CTRL0`, `CTRL1`, `STATUS`, `TOTMR`, and `BURST`.
- PLCA field masks include ID/version, enable/reset, node count/local ID, PLCA status, transmit opportunity timer, maximum burst count, and burst timer.
- `OATC14_IDM` names the expected PLCA MAP identifier.
- Advanced diagnostic registers include `MDIO_OATC14_ADFCAP`, `MDIO_OATC14_HDD`, `MDIO_OATC14_DCQ_SQI`, and `MDIO_OATC14_DCQ_SQIPLUS`.
- Diagnostic masks describe harness defect detection control/ready/start/valid/status bits, SQI/SQI+ capability and value fields, and the maximum 3-bit SQI level.
- `enum oatc14_hdd_status` translates two-bit harness defect status to cable OK, open, short, or not-detectable values.

## Control Flow And State Behavior
There is no runtime control flow or allocated state. Including drivers use these constants with MDIO MMD accessors, normally against `MDIO_MMD_VEND2`, to discover PLCA support, configure PLCA timing and node identity, start diagnostics, poll readiness, and interpret SQI or harness-defect results.

## Dependencies And Integration Points
The header depends on `<linux/mdio.h>` and common bit macros. It integrates with 10BASE-T1S PHY drivers and ethtool diagnostic reporting by providing source-of-truth field names for OPEN Alliance registers. It is intentionally separate from any one vendor driver so multiple PHY implementations can share the same ABI definitions.

## Risks And Edge Cases
- The header assumes the OPEN Alliance TC14 registers are in `MDIO_MMD_VEND2`; a PHY with nonstandard placement needs driver-specific handling.
- Field masks are raw register encodings, so users must use `FIELD_GET()`/`FIELD_PREP()` correctly.
- Diagnostic status may be valid only when the ready/valid bits are asserted; consumers must not treat stale register bits as fresh cable results.
- Specification comments include an external document reference; future spec revisions may add registers without preserving all semantics.

## Test Signals
Validation is mainly compile-time and consumer-driven: drivers should build with the header, read PLCA ID/version, enable/reset PLCA, configure NCNT/ID/timers, poll PLCA status, check SQI range 0-7, start harness diagnostics, wait for ready/valid, and map all four `oatc14_hdd_status` values to user-visible diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mdio-open-alliance.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mdio_bus.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mdio_bus.c

## Purpose
`mdio_bus.c` implements the low-level MDIO bus access API exported to PHY and MDIO device drivers. It supplies locked and caller-locked Clause 22 and Clause 45 read/write/modify helpers, device lookup helpers, tracepoint emission, and per-address bus statistics accounting.

## Important APIs, Types, And Functions
- `mdiobus_get_phy()` returns a `struct phy_device` at an address only if the registered MDIO device is flagged as a PHY.
- `mdiobus_is_registered_device()` checks address occupancy through the bus `mdio_map`.
- `__mdiobus_read()/__mdiobus_write()` are unlocked Clause 22 accessors that require `bus->mdio_lock`.
- `__mdiobus_c45_read()/__mdiobus_c45_write()` are unlocked Clause 45 accessors using `read_c45`/`write_c45`.
- `mdiobus_read()/write()`, `mdiobus_c45_read()/write()`, and `_nested` variants take the bus lock around the corresponding unlocked operation.
- `__mdiobus_modify_changed()`, `mdiobus_modify()`, `mdiobus_modify_changed()`, `mdiobus_c45_modify()`, and `mdiobus_c45_modify_changed()` implement read/modify/write with changed/no-change reporting where exposed.
- `mdiobus_stats_acct()` updates transfers, errors, reads, and writes in `struct mdio_bus_stats` using `u64_stats` synchronization.

## Control Flow And State Behavior
Every bus operation validates that `addr < PHY_MAX_ADDR`, checks whether the bus supplies the relevant access method, performs the controller callback, emits `trace_mdio_access`, and updates the per-address stats. Public helpers take `bus->mdio_lock` with either normal or nested lock class; internal `__` helpers assert the lock is held. Modify helpers read first, merge `(old & ~mask) | set`, avoid writes when unchanged, and either return a changed indicator or collapse success to zero.

The file persists no independent state beyond updating `bus->stats[addr]`. It does not register devices or buses; it assumes `struct mii_bus` was initialized by provider code and that `mdio_map` is owned by registration logic.

## Dependencies And Integration Points
The file depends on Linux device, module, mutex/lockdep, tracepoint, MII, PHY, and `u64_stats` APIs. It integrates with hardware MDIO controller drivers through `struct mii_bus` callback pointers, with phylib through exported register accessors, with tracing through `trace/events/mdio.h`, and with sysfs statistics exposed by `mdio_bus_provider.c`.

## Risks And Edge Cases
- The unlocked accessors must not be called without the lock; lockdep assertions catch this in debug builds.
- MDIO callbacks may sleep or wait for interrupts, so the documented no-interrupt-context rule matters.
- Missing read/write callback pairs return `-EOPNOTSUPP`; provider registration also rejects incomplete pairs.
- Address validation guards only upper bound; call sites should not pass negative addresses.
- Stats update paths run with preemption disabled and must remain short.

## Test Signals
Test signals include tracepoint records for reads/writes, stats incrementing per address and globally, changed/no-change modify behavior, nested access under muxed/nested MDIO buses, callback absence returning `-EOPNOTSUPP`, address 32+ returning `-ENXIO`, and lockdep warnings if unlocked helpers are misused.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mdio_bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mdio_bus_provider.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mdio_bus_provider.c

## Purpose
`mdio_bus_provider.c` implements the provider side of the MDIO bus framework: `mii_bus` allocation/free, bus and class objects, sysfs statistics attributes, bus/device matching, auto-scanning for PHYs, firmware-node association, reset GPIO handling, registration/unregistration, and bus lookup by name or OF node.

## Important APIs, Types, And Functions
- `mdiobus_alloc_size()` allocates `struct mii_bus`, optional private storage, default polling IRQ values, initial bus state, and `u64_stats` sync points.
- `mdio_bus_class` owns bus devices under the `mdio_bus` class and releases buses through `mdiobus_release()`.
- `mdio_bus_type` provides MDIO device matching, per-device statistics groups, and OF uevent modalias support.
- Sysfs helpers and generated attributes expose aggregate and per-address `transfers`, `errors`, `writes`, and `reads`.
- `mdiobus_scan()`, `mdiobus_scan_c22()`, and the private C45 scanner create PHY devices through `get_phy_device()` and register them.
- `__mdiobus_register()` validates bus operations, registers the bus device, initializes locks, toggles optional bus reset GPIO, runs bus reset, scans C22 then optionally C45, and publishes the registered state.
- `mdiobus_unregister()`, `mdiobus_free()`, `mdio_find_bus()`, and `of_mdio_find_bus()` manage lifecycle and lookup.

## Control Flow And State Behavior
Bus allocation leaves the bus in `MDIOBUS_ALLOCATED`. Registration validates that read/write callbacks are paired and that at least one access mode exists, sets device parent/class/name, pins firmware-node references for fresh buses, registers the bus device, initializes locks, handles optional bus-level reset GPIO delays, invokes `bus->reset`, scans unmasked addresses for Clause 22 PHYs, avoids Clause 45 scan if a known-bad Clause 22 PHY family is present, then scans Clause 45 if supported. On errors it removes/free any devices inserted into `mdio_map`, reasserts reset GPIO, and deletes the bus device.

The bus owns persistent in-memory state: device identity, lock objects, `mdio_map`, per-address stats, reset GPIO, state enum, owner module, and firmware-node reference. Firmware-node association for auto-probed PHYs searches child nodes by `reg`, including nested `ethernet-phy-package`, and also supports software nodes named `ethernet-phy@<addr>`.

## Dependencies And Integration Points
The file depends on driver core class/bus APIs, OF/fwnode helpers, GPIO descriptors, phylib internals, Micrel OUI definitions for C45-scan avoidance, and the MDIO device layer. It integrates with controller drivers via `mdiobus_register()`, with DT/OF through `of_mdio_find_bus()` and auto-probed PHY node linking, with `mdio_bus.c` stats, and with module matching through `mdio_bus_type.match`.

## Risks And Edge Cases
- State transitions must remain ordered; freeing a registered bus or unregistering an unregistered bus triggers warnings.
- C45 scan can disturb some C22 PHYs, so the Micrel OUI prevention path is a bus-safety behavior, not an optimization.
- `device_register()` failure paths and GPIO reset handling must not leak fwnode references or leave PHYs out of reset unintentionally.
- Auto-scanning only finds devices identifiable as PHYs; non-PHY MDIO devices must come from explicit firmware enumeration.
- The generated per-address sysfs attribute list is large and tied to `PHY_MAX_ADDR == 32`.

## Test Signals
Useful validation includes allocation with/without private data, registration rejection for incomplete callbacks, C22 and C45 scan coverage, DT child and `ethernet-phy-package` matching, software-node matching, reset GPIO assertion/deassertion timing, unregister removing all `mdio_map` entries, lookup by class name and OF node, aggregate/per-address statistics files, and C45-scan suppression when a problematic C22 PHY is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mdio_bus_provider.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mdio_device.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mdio_device.c

## Purpose
`mdio_device.c` implements the driver-core object model for MDIO devices other than the bus itself. It creates/registers/removes generic MDIO devices, manages PHY reset GPIO/reset-controller resources, maps devices into `mii_bus->mdio_map`, and registers `mdio_driver` instances on the `mdio_bus_type`.

## Important APIs, Types, And Functions
- `mdio_device_create()` allocates and initializes a `struct mdio_device`, attaches it to a bus, assigns release/remove/free callbacks, sets the address, and initializes the device name.
- `mdio_device_register()` inserts the device into the bus map and calls `device_add()`.
- `mdio_device_remove()` performs `device_del()` and unregisters the address mapping.
- `mdio_device_free()` drops the device reference; `mdio_device_release()` frees the object and fwnode reference at final release.
- `mdiobus_register_device()` and `mdiobus_unregister_device()` own `bus->mdio_map[addr]` and reset-resource setup/teardown.
- `mdio_device_reset()` asserts/deasserts optional reset GPIO and reset controller signals with configured delays.
- `mdio_driver_register()` and `mdio_driver_unregister()` connect `struct mdio_driver` callbacks to driver-core probe/remove/shutdown wrappers.

## Control Flow And State Behavior
Device creation initializes the embedded `struct device` but does not publish it. Registration first rejects occupied addresses. For PHY-flagged devices, it obtains optional `reset` GPIO and exclusive `phy` reset control, reads `reset-assert-us` and `reset-deassert-us`, and asserts reset before mapping the device into the bus. `device_add()` then triggers matching/probe. The MDIO probe wrapper deasserts reset before calling the driver probe and reasserts it on probe failure. Remove calls the driver remove hook and reasserts reset.

Persistent state is the `struct mdio_device` itself: bus pointer, address, reset GPIO/control pointers, reset state, delay values, flags, and driver callbacks. There is no disk persistence; firmware properties and reset providers are the external source of reset behavior.

## Dependencies And Integration Points
The file depends on Linux device core, GPIO descriptors, reset controller APIs, firmware property helpers, `linux/mdio.h`, `linux/phy.h`, and phylib internals. It integrates directly with `mdio_bus_provider.c` via `mdio_bus_type` and `mii_bus->mdio_map`, with PHY creation/registration paths, and with non-PHY MDIO drivers through `mdio_driver_register()`.

## Risks And Edge Cases
- Address registration is not internally locked here; callers rely on bus registration/lifecycle serialization.
- Reset resources are only acquired for devices flagged as PHYs. Non-PHY MDIO devices need their own reset handling if required.
- Probe failure reasserts reset, but drivers must still clean up any resources allocated before returning an error.
- `mdiobus_unregister_device()` returns `-EINVAL` if the map does not point to the same object, protecting against double or wrong-device removal.
- Reset delays use firmware-provided microsecond values; missing or incorrect properties can expose hardware timing issues.

## Test Signals
Test creation/register/remove/free ordering, duplicate address returning `-EBUSY`, reset GPIO/control assertion on registration and removal, deassertion before probe, reassertion on probe failure, property-driven reset delays, driver registration/unregistration, shutdown callback dispatch, and `mdio_map` clearing after remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mdio_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mdio_devres.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mdio_devres.c

## Purpose
`mdio_devres.c` provides device-managed helpers for allocating and registering MDIO buses. It lets MDIO bus provider drivers bind bus cleanup to the lifetime of their parent `struct device`, reducing manual error-path and detach cleanup.

## Important APIs, Types, And Functions
- `struct mdiobus_devres` stores the managed `struct mii_bus *`.
- `devm_mdiobus_alloc_size()` wraps `mdiobus_alloc_size()` and registers a devres action that calls `mdiobus_free()`.
- `__devm_mdiobus_register()` wraps `__mdiobus_register()` and registers a devres action that calls `mdiobus_unregister()`.
- `__devm_of_mdiobus_register()` conditionally wraps `__of_mdiobus_register()` when `CONFIG_OF_MDIO` is enabled.
- `mdiobus_devres_match()` verifies that a bus being registered was previously allocated by the matching managed allocation helper.

## Control Flow And State Behavior
Managed allocation creates a devres record, allocates the bus, stores it, and attaches the record to the parent device. Managed registration first checks that a matching allocation devres exists, allocates a second devres record for unregister, calls the underlying registration function, then stores the bus in the unregister record. On parent-device detach, devres unwinds in reverse order: unregister runs before free when both records were added normally.

The file persists no global state. Its only state is devres-managed records attached to parent devices. The underlying bus state transitions remain owned by `mdio_bus_provider.c`.

## Dependencies And Integration Points
The file depends on devres, phylib MDIO allocation/register APIs, and optional OF MDIO registration. It integrates with MDIO controller drivers that prefer `devm_mdiobus_alloc_size()`, `devm_mdiobus_register()`, or `devm_of_mdiobus_register()` wrappers exposed through headers/macros.

## Risks And Edge Cases
- Managed registration deliberately fails with `-EINVAL` if the bus was not allocated through the managed helper for that device, preventing mismatched cleanup ownership.
- If registration fails, the unregister devres record is freed and only the allocation/free record remains.
- Devres unwind ordering is important; manually unregistering/freeing a managed bus without removing devres would risk double cleanup.
- The OF helper exists only under `CONFIG_OF_MDIO`.

## Test Signals
Validate allocation failure returns `NULL`, managed registration rejects unmanaged buses, failed registration does not add unregister devres, successful detach unregisters before free, OF registration behaves the same under `CONFIG_OF_MDIO`, and parent-driver probe error unwinds leave no registered bus or leaked `mii_bus`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mdio_devres.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/Kconfig

## Purpose
`mediatek/Kconfig` defines the configuration symbols for MediaTek and Airoha PHY drivers and their shared helper library. It controls which PHY objects are built, their architecture dependencies, and the shared support selected by the individual drivers.

## Important APIs, Types, And Symbols
- `MEDIATEK_2P5GE_PHY` builds the MT7988 built-in 2.5GbE PHY driver. It depends on `ARM64 && ARCH_MEDIATEK` or `COMPILE_TEST` and selects `MTK_NET_PHYLIB`.
- `MEDIATEK_GE_PHY` builds the non-built-in gigabit PHY driver, including MT7530/MT7531-style PHYs, and selects `MTK_NET_PHYLIB`.
- `MEDIATEK_GE_SOC_PHY` builds SoC built-in gigabit PHY support for MT7981/MT7988 and Airoha variants. It depends on ARM64 or compile testing, requires Airoha or MediaTek efuse-capable platforms unless compile-testing, and selects both `MTK_NET_PHYLIB` and `PHY_PACKAGE`.
- `MTK_NET_PHYLIB` is a hidden tristate used for shared MediaTek PHY helper code.

## Control Flow And State Behavior
This file has no runtime control flow. At configuration time it determines whether the relevant drivers can be selected and whether shared helper objects are included. The selected symbols affect compilation of `mtk-2p5ge.o`, `mtk-ge.o`, `mtk-ge-soc.o`, and `mtk-phy-lib.o` through the adjacent Makefile.

## Dependencies And Integration Points
The symbols integrate with Kbuild, phylib, MediaTek/Airoha architecture symbols, NVMEM efuse support, and PHY package support. The help text documents firmware loading for 2.5GbE PHYs and efuse-driven calibration for SoC gigabit PHYs, matching the behavior in the C sources.

## Risks And Edge Cases
- `MEDIATEK_GE_SOC_PHY` has platform and NVMEM dependencies because calibration data may be required for correct analog behavior.
- `COMPILE_TEST` broadens build coverage but does not imply runtime platform support.
- The hidden `MTK_NET_PHYLIB` must be selected by every driver that uses shared `mtk.h`/helper functions; missing selection would produce link failures.
- `PHY_PACKAGE` is required for shared MT7988 package state in `mtk-ge-soc.c`.

## Test Signals
Build-test the symbols as built-in and modules, with and without `COMPILE_TEST`, and verify dependencies pull in `mtk-phy-lib.o` and `PHY_PACKAGE` where required. Confirm invalid platform combinations hide the SoC PHY option outside compile-test configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/Makefile

## Purpose
`mediatek/Makefile` maps the MediaTek PHY Kconfig symbols to kernel objects. It is the build glue for the driver sources and the shared helper library in this directory.

## Important APIs, Types, And Targets
- `obj-$(CONFIG_MEDIATEK_2P5GE_PHY) += mtk-2p5ge.o` builds the 2.5GbE SoC PHY driver.
- `obj-$(CONFIG_MEDIATEK_GE_PHY) += mtk-ge.o` builds the non-built-in gigabit PHY driver.
- `obj-$(CONFIG_MEDIATEK_GE_SOC_PHY) += mtk-ge-soc.o` builds the SoC gigabit PHY/Airoha driver.
- `obj-$(CONFIG_MTK_NET_PHYLIB) += mtk-phy-lib.o` builds the shared MediaTek PHY helper library.

## Control Flow And State Behavior
There is no runtime state or control flow. Kbuild evaluates each `obj-$()` expression from `.config` and includes the corresponding object either built-in, as a module, or not at all. The shared helper object is controlled by the hidden `MTK_NET_PHYLIB` symbol selected by the driver Kconfig entries.

## Dependencies And Integration Points
The Makefile integrates directly with the Kconfig file in the same directory and with the broader `drivers/net/phy` build. It also codifies that both `mtk-2p5ge.c` and `mtk-ge-soc.c` depend on helper routines supplied by `mtk-phy-lib.o`.

## Risks And Edge Cases
- If a driver uses shared helper symbols without selecting `MTK_NET_PHYLIB`, module or vmlinux linking will fail.
- Object names must match source files; adding a new driver requires corresponding Kconfig and Makefile updates.
- Built-in versus module combinations need consistent symbol visibility for shared helpers.

## Test Signals
Build all four symbols as modules, all as built-ins, and individual driver combinations to confirm `mtk-phy-lib.o` is included exactly when needed and no unresolved symbols are emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/mtk-2p5ge.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/mtk-2p5ge.c

## Purpose
`mtk-2p5ge.c` implements the MediaTek MT7988 built-in 2.5GbE PHY driver. It loads required PHY MCU firmware into a fixed PMB memory window, configures internal PHY tuning, handles Clause 45 autonegotiation with Clause 22 1000BASE-T supplements, reports link speed through vendor auxiliary status, exposes pause-based rate matching, and provides LED control through shared MediaTek PHY helper functions.

## Important APIs, Types, And Functions
- `mt798x_2p5ge_phy_load_fw()` maps PMB and MCU CSR address ranges, validates and copies `mediatek/mt7988/i2p5ge-phy-pmb.bin`, stalls/restarts the PHY MCU, and resets the PHY.
- `mt798x_2p5ge_phy_probe()` patches missing C45 MMD presence bits, loads firmware, programs default LED behavior, switches LED pinctrl, allocates `struct mtk_socphy_priv`, and initializes LED state.
- `mt798x_2p5ge_phy_config_init()` requires `PHY_INTERFACE_MODE_INTERNAL`, tunes LPI threshold, enables a token-ring next-page setting, and enables hardware downshift.
- `mt798x_2p5ge_phy_config_aneg()` combines `genphy_c45_an_config_aneg()` with Clause 22 `MII_CTRL1000` advertisement programming.
- `mt798x_2p5ge_phy_get_features()` reads C45 PMA abilities and removes unsupported 100baseT half-duplex.
- `mt798x_2p5ge_phy_read_status()` uses C22 link update, C45 LPA plus C22 1G LPA, and vendor auxiliary speed bits.
- LED callbacks delegate blink, brightness, and hardware control to shared `mtk_phy_*` helpers.

## Control Flow And State Behavior
Probe is firmware-first: it ensures the hardware's incomplete MMD discovery is corrected, loads firmware via direct firmware request, initializes LED registers, selects LED pinmux, allocates private LED/helper state, and registers LED state with the shared library. Firmware loading powers the PHY down, writes host commands to stall the MCU, copies the exact-size firmware image to PMB memory, toggles `MD32_EN`, resets the PHY, waits for stabilization, and logs firmware date/version.

At config time the PHY must be connected through an internal interface. Autonegotiation is mostly Clause 45 but 1000BASE-T advertisement and partner advertisement are handled through Clause 22 because this hardware design exposes that mode there. Link status avoids generic C45 link status because the C45 bit can assert before AN is actually complete; it uses `genphy_update_link()` and reads speed from `PHY_AUX_CTRL_STATUS`. Runtime state is limited to devres mappings during firmware load, firmware-programmed hardware, and `phydev->priv`.

## Dependencies And Integration Points
The driver depends on firmware loading, fixed SoC MMIO mappings via `ioremap()`, phylib C22/C45 helpers, pinctrl state `i2p5gbe-led`, shared MediaTek helper functions from `mtk-phy-lib`, and `struct mtk_socphy_priv` from `mtk.h`. It integrates with Kbuild through `MODULE_FIRMWARE()` and the `MEDIATEK_2P5GE_PHY` symbol.

## Risks And Edge Cases
- Firmware size must match exactly; wrong firmware fails probe.
- Fixed physical MMIO addresses assume MT7988 SoC integration and are not discoverable resources.
- The firmware copy casts firmware bytes to `uint32_t *`, so alignment and endian expectations are hardware-specific.
- Missing LED pinctrl only logs an error; the PHY can still probe with nonfunctional LEDs.
- Ignored return values in some setup writes mean later failures may surface as link issues rather than probe errors.
- Link reporting depends on vendor auxiliary speed bits.

## Test Signals
Validate firmware present/missing/wrong-size cases, MCU restart and reset timing, internal-interface rejection for non-internal modes, C45 MMD presence patching, 10/100/1000/2500 link reporting, C22 1G advertisement and LPA handling, pause rate matching, LED0/LED1 defaults, LED triggers and brightness control, suspend/resume, and module firmware metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/mtk-2p5ge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/mtk-ge-soc.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/mtk-ge-soc.c

## Purpose
`mtk-ge-soc.c` implements MediaTek/Airoha SoC gigabit PHY support for MT7981, MT7988, AN7581, and AN7583. The driver focuses on analog/DSP tuning, efuse and software calibration, LED control, shared MT7988 package state, and minimal interrupt handling through generic no-ack phylib helpers.

## Important APIs, Types, And Functions
- `struct mtk_socphy_shared` stores package-wide MT7988 boottrap polarity data and per-address `struct mtk_socphy_priv` records.
- Calibration helpers include `cal_cycle()`, `rext_*`, `tx_offset_*`, `tx_amp_*`, `tx_r50_*`, `tx_vcm_cal_sw()`, `cal_efuse()`, `cal_sw()`, `start_cal()`, and `mt798x_phy_calibration()`.
- Fine-tuning paths include `mt798x_phy_common_finetune()`, `mt7981_phy_finetune()`, `mt7988_phy_finetune()`, and `mt798x_phy_eee()`.
- Probe paths are `mt7981_phy_probe()`, `mt7988_phy_probe()`, `mt7988_phy_probe_shared()`, and `an7581_phy_probe()`.
- LED operations include `mt798x_phy_led_blink_set()`, `mt798x_phy_led_brightness_set()`, hardware-trigger get/set/is-supported helpers, MT7988 LED polarity boottrap handling, and `an7581_phy_led_polarity_set()`.
- `mtk_socphy_driver[]` maps exact PHY IDs to phylib callbacks.

## Control Flow And State Behavior
For MT7981/MT7988, probe allocates or joins private state, initializes shared LED state, and runs calibration. MT7988 joins a PHY package for addresses 0-3, reads a package-level GPIO boottrap register through a `mediatek,pio` phandle once, uses the captured bits to set LED0 polarity per PHY, applies LED pinctrl, disables TX power saving to satisfy compliance and support TX-VCM calibration, then calibrates. MT7981 uses per-device private state and calibration. Airoha AN7581/AN7583 probe mainly sets LED pinctrl and private state; AN7583 additionally clears `BMCR_PDOWN` in `config_init`.

`mt798x_phy_config_init()` applies chip-specific finetune tables, common token-ring/DSP tuning, EEE tuning, and calibration. Calibration reads an NVMEM cell named `phy-cal-data`, validates four nonzero words, applies efuse-backed REXT/TX offset/TX amplitude/TX R50 values, and runs software TX-VCM calibration on pair A. `tx_vcm_cal_sw()` performs a binary-search-like calibration over TX reserve settings using analog comparator cycles and restores calibration control bits before returning. State is stored in MDIO MMD registers, token-ring debug nodes, NVMEM-derived values, and package private memory.

## Dependencies And Integration Points
The driver depends on phylib, `PHY_PACKAGE`, NVMEM cell APIs, regmap/syscon, OF phandles, pinctrl, shared MediaTek helper functions, token-ring debug accessors, and generic PHY interrupt helpers. It integrates with board firmware through `phy-cal-data`, `mediatek,pio`, and `gbe-led` pinctrl, with LEDs through phylib LED hooks, and with Kconfig dependencies on Airoha/MediaTek platforms.

## Risks And Edge Cases
- Calibration quality depends on valid efuse data. Missing NVMEM is tolerated, but malformed or zero data returns errors.
- Many finetune constants are silicon-specific magic values; changing them requires hardware validation.
- MT7988 package sharing assumes MDIO addresses 0-3 and a valid `mediatek,pio` phandle.
- Calibration functions often perform several MDIO writes and may leave analog state altered if a lower-level helper silently fails.
- LED polarity depends on boottrap pins shared with LEDs; configuring pinctrl too early can cause bogus blinking or wrong polarity.
- `tx_vcm_cal_sw()` has narrow timing limits and reports low/high margin warnings that should be treated as signal-quality risks.

## Test Signals
Test exact PHY ID matching for all four devices, MT7988 package join/probe-once behavior, invalid address rejection, `mediatek,pio` missing/error paths, NVMEM defer/missing/invalid/valid cases, calibration success and timeout handling, MT7981 versus MT7988 finetune register writes, AN7583 power-down clearing, LED polarity modes, LED hardware triggers, no-ack interrupt path, suspend/resume, and link stability/EEE behavior after calibration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mediatek/mtk-ge-soc.c -->
