<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_mdio.h -->
# sources/distributed-fs/ceph-client/include/linux/acpi_mdio.h

## Purpose
`acpi_mdio.h` provides an ACPI-aware MDIO bus registration wrapper for Ethernet PHY buses.

## Important APIs, types, and functions
When `CONFIG_ACPI_MDIO` is enabled, `__acpi_mdiobus_register()` registers an MDIO bus with a firmware node and owner module, while `acpi_mdiobus_register()` wraps it with `THIS_MODULE`. When disabled, `acpi_mdiobus_register()` falls back to ordinary `mdiobus_register()`.

## Control flow
Network drivers call the wrapper during probe. Enabled builds register with ACPI child/PHY discovery; disabled builds use generic MDIO registration to keep drivers source-compatible.

## State and persistence behavior
The MDIO core owns bus and PHY device state after registration. The header adds no persistent state.

## Dependencies and integration points
It depends on `linux/phy.h`, `struct mii_bus`, fwnodes, modules, and MDIO/PHY registration.

## Risks and test signals
Risks include owner-module mismatch, missing ACPI PHY discovery, and fallback behavior hiding ACPI-specific probe failures. Test signals include ACPI-described PHY enumeration, non-ACPI MDIO registration, module unload, and builds with/without `CONFIG_ACPI_MDIO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_mdio.h -->
