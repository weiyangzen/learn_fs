<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/fwnode_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/fwnode_mdio.c

Purpose: provides firmware-node-neutral helpers to create and register PHY devices on MDIO buses from OF or ACPI child nodes, including optional PSE and timestamping integration.

Important APIs/types/functions: exports `fwnode_mdiobus_phy_device_register` and `fwnode_mdiobus_register_phy`. Internal helpers are `fwnode_find_pse_control` and `fwnode_find_mii_timestamper`.

Control flow: PHY registration reads IRQs with defer-state fallback, handles `broken-turn-around`, attaches the fwnode to the PHY device, and calls `phy_device_register`. Higher-level registration discovers a timestamper, detects C45 compatibility or explicit PHY IDs, obtains/creates a `phy_device`, handles ACPI and OF registration paths, binds optional PSE control, and assigns timestamping when available.

State and persistence: state lives in registered `phy_device` instances: IRQ, fwnode reference, `psec`, `mii_ts`, and bus masks. Error paths remove/free PHYs and unregister timestampers.

Dependencies/integration: depends on phylib, generic firmware nodes, OF helpers for timestampers and PSE, ACPI checks, IRQ firmware lookup, and PHY device lifecycle APIs.

Risks and test signals: risks include leaked fwnode/timestamper references on error, wrong C45 detection, IRQ probe deferral behavior, and optional PSE errors after PHY registration. Tests should cover ACPI and OF paths, explicit PHY IDs, missing IRQ providers, PSE/timestamper defer/fail cases, and `broken-turn-around` masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/fwnode_mdio.c -->
