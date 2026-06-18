# sources/distributed-fs/ceph-client/drivers/net/mdio/of_mdio.c

## Purpose
This file provides OpenFirmware/device-tree helpers for MDIO and Ethernet PHY registration. It bridges OF nodes to the generic firmware-node MDIO helpers, populates `mii_bus` instances from child nodes, supports fixed-link PHY binding compatibility, and exposes convenience APIs for network drivers to find and connect PHY devices described in the device tree.

## Important APIs, Types, and Functions
Exported entry points include `of_mdiobus_phy_device_register()`, `of_mdiobus_child_is_phy()`, `__of_mdiobus_register()`, `of_mdio_find_device()`, `of_phy_find_device()`, `of_phy_connect()`, `of_phy_get_and_connect()`, `of_phy_is_fixed_link()`, `of_phy_register_fixed_link()`, and `of_phy_deregister_fixed_link()`. Internal helpers route through firmware-node APIs such as `fwnode_get_phy_id()`, `fwnode_mdiobus_register_phy()`, `fwnode_mdiobus_phy_device_register()`, `fwnode_mdio_find_device()`, and `fwnode_phy_find_device()`. The `whitelist_phys[]` table recognizes legacy PHY compatible strings that should not be used for real driver matching.

## Control Flow
`__of_mdiobus_register()` handles the main bus setup. If no OF node is supplied it delegates to `__mdiobus_register()`. For an OF node, it rejects disabled nodes, masks automatic PHY probing, attaches the OF fwnode to the bus device, reads optional reset delays, registers the bus, then parses child nodes. `__of_mdiobus_parse_phys()` recursively descends valid `ethernet-phy-package` nodes, parses each child address with `of_mdio_parse_addr()`, classifies children as PHYs or generic MDIO devices, and registers the appropriate device type. If a child lacks a valid `reg`, the caller can request a scan; the later scan attempts all PHY addresses for nodes without `reg`, skipping already registered devices and stopping when a PHY registers successfully. The PHY connect helpers find a PHY node or fixed-link node, connect through `phy_connect_direct()`, then drop the lookup reference.

## State and Persistence
The file stores no global mutable state beyond constant match tables. It mutates `mii_bus` fields such as `phy_mask`, bus fwnode, and reset delays during registration. Registered MDIO, PHY, and fixed PHY devices persist in kernel device state until bus unregister or explicit fixed-link deregistration. Reference handling is important: find helpers return devices with elevated refcounts, and connect helpers balance the temporary lookup reference after `phy_connect_direct()`.

## Dependencies and Integration Points
Dependencies include OF core, OF IRQ, OF net helpers, PHYLIB, fixed PHY support, netdevice APIs, module exports, and generic fwnode MDIO code. Hardware-specific MDIO bus drivers call `of_mdiobus_register()`, which maps to this implementation. Ethernet MAC drivers use `of_phy_get_and_connect()` or `of_phy_connect()` to bind a netdev to a PHY or fixed-link description.

## Risks and Edge Cases
The child classification rule treats nodes without a `compatible` property as PHYs, preserving old bindings but allowing ambiguous nodes to become PHY probes. Invalid `ethernet-phy-package` nodes without `reg` are ignored, while other invalid `reg` values can trigger a full bus scan. Deprecated array-style fixed links are accepted with a warning. Fixed links with `managed = "in-band-status"` register a zeroed status, so consumers must interpret the managed mode correctly. Errors during child registration unwind by unregistering the entire bus; errors during scan only continue for `-ENODEV`.

## Test Signals
Test coverage should include DT buses with explicit PHY `reg`, child MDIO devices with non-PHY compatibles, nested `ethernet-phy-package` nodes, children without `reg` requiring scan, disabled MDIO nodes, fixed-link new and deprecated bindings, and `managed` modes. Runtime signals are registered MDIO/PHY devices with OF fwnodes, expected link callbacks from `phy_connect_direct()`, warning logs for whitelisted/deprecated bindings, and clean unregister on parse failure.
