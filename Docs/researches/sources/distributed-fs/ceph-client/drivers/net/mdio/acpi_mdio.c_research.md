<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/acpi_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/acpi_mdio.c

Purpose: registers an MDIO bus from ACPI firmware descriptions and instantiates PHY devices from ACPI child nodes.

Important APIs/types/functions: exports `__acpi_mdiobus_register(struct mii_bus *mdio, struct fwnode_handle *fwnode, struct module *owner)`. It uses `acpi_get_local_address`, `ACPI_COMPANION_SET`, `__mdiobus_register`, and `fwnode_mdiobus_register_phy`.

Control flow: the helper masks all PHY addresses to prevent auto-probing, registers the mii_bus, associates the ACPI companion with the bus device, iterates child fwnodes, extracts each local address, filters invalid addresses, and delegates PHY creation/registration to the fwnode helper. Missing devices are logged but do not abort the whole bus registration.

State and persistence: state is in caller-owned `mii_bus`, ACPI companion references, and registered PHY devices. No driver-private persistent storage exists.

Dependencies/integration: depends on ACPI, fwnode MDIO helpers, phylib, and bus owner module registration. It is a firmware accessor library, not a platform driver.

Risks and test signals: risks include incomplete ACPI address data, silently skipped invalid children, and partial bus population after child registration failures. Tests should exercise ACPI child parsing, address bounds, deferred PHY errors, and bus registration/unregistration with ACPI companions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/acpi_mdio.c -->
