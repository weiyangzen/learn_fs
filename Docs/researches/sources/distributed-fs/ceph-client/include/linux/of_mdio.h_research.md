<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_mdio.h -->
# sources/distributed-fs/ceph-client/include/linux/of_mdio.h

## Purpose
This header declares OF helpers for registering MDIO buses, discovering PHY/MDIO devices, fixed-link handling, and connecting network devices to PHYs.

## Important APIs, types, and functions
When `CONFIG_OF_MDIO` is enabled, APIs include `of_mdiobus_child_is_phy()`, `__of_mdiobus_register()`, `of_mdiobus_register()`, `__devm_of_mdiobus_register()`, `devm_of_mdiobus_register()`, `of_mdio_find_device()`, `of_phy_find_device()`, `of_phy_connect()`, `of_phy_get_and_connect()`, `of_mdio_find_bus()`, fixed-link register/deregister/test helpers, `of_mdiobus_phy_device_register()`, and `of_mdio_parse_addr()`. The address parser reads `reg`, logs invalid addresses, and enforces `addr < PHY_MAX_ADDR`.

## Control flow
An MDIO controller registers its bus from a DT node, children are classified as PHY or MDIO devices, and network drivers locate/connect PHYs by node or fixed-link description. Devm registration binds bus cleanup to the parent device. Without OF MDIO, bus registration falls back to non-DT `mdiobus_register()`/`devm_mdiobus_register()`, while lookup/connect/fixed-link helpers return unavailable results.

## State and persistence
Bus/PHY/device registrations persist in MDIO and PHY core state. Fixed-link registrations create software PHY state tied to the node. This header itself stores no state.

## Dependencies and integration points
It depends on device, PHY/MDIO, module owner, OF property helpers, net_device, and devm APIs. It integrates Ethernet MAC drivers, MDIO controllers, PHYLIB, and fixed-link DT bindings.

## Risks and test signals
Risks include invalid `reg` addresses, child classification errors, fixed-link leaks, module owner mismatches in wrappers, fallback registration masking missing OF support, and PHY connection lifetime issues. Test MDIO bus registration with mixed child nodes, invalid addresses, fixed-link register/deregister, PHY connect/disconnect, devm cleanup, and `!CONFIG_OF_MDIO` fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_mdio.h -->
