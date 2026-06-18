<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fwnode_mdio.h -->
# sources/distributed-fs/ceph-client/include/linux/fwnode_mdio.h

Purpose: Declares fwnode-based helpers for registering Ethernet PHY devices on MDIO buses.

Important APIs/types/functions: Exposes `fwnode_mdiobus_phy_device_register()` to register a prepared `phy_device` under a child fwnode/address and `fwnode_mdiobus_register_phy()` to discover/register a PHY from a child node and MDIO address.

Control flow: MDIO bus code passes the bus, child firmware node, and PHY address. If configured, helper implementation reads fwnode properties and binds/registers the PHY device. Disabled stubs return `-EINVAL`.

State and persistence behavior: This header stores no state. Registered PHY state is owned by the PHY/MDIO subsystem and device model.

Dependencies and integration points: Depends on `<linux/phy.h>`, `mii_bus`, `phy_device`, and fwnode handles. Integrates firmware descriptions with network PHY discovery.

Risks: Disabled config stubs make callers fail registration with `-EINVAL`; optional consumers must treat this distinctly from malformed firmware. Address/property mismatches can produce missing PHYs.

Test signals: MDIO registration from ACPI/software-node/device-tree-backed fwnodes, disabled `CONFIG_FWNODE_MDIO` builds, malformed address/property tests, and PHY driver probe checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fwnode_mdio.h -->
