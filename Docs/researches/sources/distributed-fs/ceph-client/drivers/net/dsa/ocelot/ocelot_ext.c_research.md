# sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/ocelot_ext.c

## Purpose
This file is the platform/MFD front end for externally controlled Ocelot VSC7512-class switches. It provides a compact `felix_info` profile that uses parent MFD regmaps and generic VSC7514 Ocelot data, then registers the switch through the common Felix DSA library.

## Important APIs, Types, and Functions
- `VSC7514_NUM_PORTS` defines an 11-port profile.
- `vsc7512_port_modes` lists supported modes for each port: ports 0-3 are internal, ports 4-8 and 10 support SGMII/QSGMII, and port 9 supports SGMII.
- `ocelot_ext_ops` supplies generic Ocelot reset, watermark, stats conversion, and Felix netdev/port translation callbacks.
- `vsc7512_resource_names` maps Ocelot targets to parent MFD regmap names.
- `vsc7512_info` supplies regfields, regmap, VCAP props, MAC table size, port count, port modes, MAC config, and serdes configuration callbacks.
- `ocelot_ext_probe()` calls `felix_register_switch()` with switch base 0, one flooding PGID, PTP disabled, MAC Merge disabled, initial `DSA_TAG_PROTO_OCELOT`, and `vsc7512_info`.
- `ocelot_ext_remove()` unregisters the DSA switch.
- `ocelot_ext_shutdown()` calls `dsa_switch_shutdown()` and clears driver data.

## Control Flow
The platform driver binds to `mscc,vsc7512-switch`. Probe delegates almost all setup to `felix_register_switch()` and the shared Felix setup path. Because `vsc7512_info.resources` is null, the shared library requests regmaps from the parent MFD device by the names listed in `vsc7512_resource_names` rather than creating new MMIO regmaps from static resources.

Remove retrieves `struct felix` from driver data and unregisters the DSA switch. Shutdown performs DSA switch shutdown and clears the platform device driver data.

## State and Persistence Behavior
This file has no private mutable runtime state beyond driver data created by `felix_register_switch()`. Hardware/runtime state lives in the shared `struct felix` and embedded `struct ocelot`. Static mode tables and resource names are immutable. No state is persisted across unbind or reboot.

## Dependencies and Integration Points
The driver depends on `MFD_OCELOT` parent regmaps, generic Ocelot VSC7514 register/VCAP definitions, platform device probing, DSA, and the shared Felix library. It imports the `MFD_OCELOT` namespace and relies on device tree compatibility `mscc,vsc7512-switch`.

## Risks and Edge Cases
- The file name and help text mention multiple VSC7511-7514 chips, but the OF match shown here is only `mscc,vsc7512-switch`; other compatibles must be provided elsewhere or are unsupported by this front end.
- Resource-name mismatches between MFD parent and this child prevent regmap lookup during Felix setup.
- PTP and MAC Merge are disabled in `felix_register_switch()` arguments; enabling them would require additional caps, IRQ, and register support.
- Port mode table must match board/device-tree wiring or Felix DT parsing will skip unsupported ports.

## Test Signals
Test with an MFD Ocelot parent exposing all named regmaps, device-tree `ports`/`ethernet-ports` nodes with valid PHY modes, DSA registration and unregister, basic bridge/VLAN/FDB/MDB operations through the shared Felix layer, and failure cases for missing parent regmaps or invalid port modes.
