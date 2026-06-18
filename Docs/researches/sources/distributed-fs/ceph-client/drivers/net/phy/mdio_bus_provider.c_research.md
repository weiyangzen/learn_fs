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
