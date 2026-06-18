<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio/mdio-regmap.h -->
# sources/distributed-fs/ceph-client/include/linux/mdio/mdio-regmap.h

## Purpose
This header defines a devm-managed MDIO bus adapter for devices whose internal PHY or PCS registers are exposed through a regmap.

## Important APIs, types, and functions
`struct mdio_regmap_config` contains parent device, regmap, bus name, one valid address, and `autoscan` flag. `devm_mdio_regmap_register()` registers a managed `mii_bus` using that config.

## Control flow
A driver fills the config and calls the devm helper. MDIO operations are translated to regmap reads/writes, optionally scanning addresses depending on configuration. Device-managed cleanup unregisters the bus on driver detach.

## State and persistence
Runtime state is in the registered bus and regmap-backed hardware. The header stores none.

## Dependencies and integration points
It depends on phylib, device-managed resources, and regmap. It integrates internal PHY/PCS blocks inside MMIO devices with generic MDIO consumers.

## Risks and test signals
Risks include invalid address filtering, duplicate bus names, regmap access failures, autoscan discovering unintended devices, and devm cleanup ordering. Test valid and invalid addresses, autoscan enabled/disabled, read/write translation, and detach cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio/mdio-regmap.h -->
