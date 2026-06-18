# sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/seville_vsc9953.c

## Purpose

This file is the DSA platform driver for the Microchip/Microsemi VSC9953 "Seville" switch block, using the shared Ocelot/Felix infrastructure. It describes the VSC9953 register layout, VCAP capabilities, port modes, reset sequence, internal MDIO/PCS discovery, and the platform probe/remove/shutdown hooks that register the switch as a Felix-backed DSA device with `DSA_TAG_PROTO_SEVILLE`.

## Important APIs, Types, and Data

- `VSC9953_NUM_PORTS` is 10. Ports 0-7 support serial PCS modes (`1000BASEX`, `SGMII`, `QSGMII`), while ports 8-9 are internal.
- `vsc9953_*_regmap` arrays map Ocelot logical registers for ANA, QS, VCAP, QSYS, REW, SYS, GCB, and DEV_GMII targets to VSC9953 offsets. Unsupported registers are explicitly reserved.
- `vsc9953_resources` and `vsc9953_resource_names` describe the target memory windows relative to the platform resource base. These are consumed by `felix_register_switch()`.
- `vsc9953_regfields` maps shared Ocelot regfield IDs to VSC9953 bit positions, including reset, MAC-table, pause, extraction/injection header, and per-port switch mode fields.
- `vsc9953_vcap_*_keys`, `vsc9953_vcap_*_actions`, and `vsc9953_vcap_props` describe ES0, IS1, and IS2 key/action widths and target blocks for Ocelot VCAP handling.
- `vsc9953_ops` implements the `struct ocelot_ops` hooks for reset, watermark encode/decode/stat parsing, and Felix netdev/port translation.
- `seville_info_vsc9953` is the central `struct felix_info` instance tying together resources, register maps, regfields, VCAP, policer ranges, MAC-table size, port count, quirks, MDIO callbacks, and port modes.

## Control Flow

Probe starts in `seville_probe()`, validates the platform memory resource, and calls `felix_register_switch(dev, res->start, 1, false, false, DSA_TAG_PROTO_SEVILLE, &seville_info_vsc9953)`. Felix then uses the static metadata in this file to map target windows, initialize Ocelot state, reset the switch, and register the DSA switch.

The reset hook `vsc9953_reset()` soft-resets the switch core through `GCB_SOFT_RST_SWC_RST`, waits for the bit to clear, enables and triggers SYS memory initialization, waits for `SYS_RESET_CFG_MEM_INIT` to clear, then enables the switch core with `SYS_RESET_CFG_CORE_ENA`. Polling uses `readx_poll_timeout()` via small status helpers.

MDIO setup is handled by `vsc9953_mdio_bus_alloc()`. It allocates `felix->pcs`, creates an internal MIIM bus through `mscc_miim_setup()` using GCB registers, registers that bus with OF MDIO helpers, and then scans non-unused, non-internal ports for Lynx PCS devices at internal MDIO addresses `port + 4`. `vsc9953_mdio_bus_free()` destroys any created PCS objects; bus unregister/free are device-managed.

Remove and shutdown are DSA lifecycle wrappers. `seville_remove()` calls `dsa_unregister_switch()` when a Felix instance exists. `seville_shutdown()` calls `dsa_switch_shutdown()` and clears platform drvdata.

## State and Persistence

Persistent runtime state is held by the Felix/Ocelot core, not by file-local mutable globals. This file contributes static hardware description tables. Runtime state created here includes the device-managed internal MDIO bus, the `felix->pcs` array, and per-port Lynx PCS instances. Hardware state persists in switch registers until reset/shutdown, including VCAP entries, MAC table, pause configuration, and port modes configured by the Ocelot/Felix stack.

## Dependencies and Integration Points

The driver depends on Linux platform devices, OF matching, DSA, phylink PCS, `pcs-lynx`, `mdio-mscc-miim`, and the Ocelot/Felix common driver. It integrates with DSA via `felix_register_switch()`, with Ocelot through register maps/regfields/VCAP props, and with internal SerDes/PCS through an MDIO bus. The OF compatible string is `mscc,vsc9953-switch`.

## Risks and Edge Cases

The largest risk is register-description accuracy: bad offsets, field widths, or resource names can silently corrupt switch configuration. Reset sequencing depends on timeout constants and assumes GCB/SYS bits behave as expected. PCS discovery ignores failed `lynx_pcs_create_mdiodev()` calls per port, which allows partial operation but can obscure missing PCS instances. Port-mode mismatch in device tree can leave serial ports without PCS support. The watermark encoder warns on values outside the representable range but still returns an encoded value, so callers must respect hardware limits.

## Test Signals

Useful signals are successful platform probe on a `mscc,vsc9953-switch` node, DSA switch registration with 10 ports, internal MDIO bus registration, "Found PCS" messages for active serial ports, successful link-up over SGMII/QSGMII/1000BASE-X, VCAP rule programming through switchdev/tc, FDB learning, bridge/VLAN behavior through the Ocelot stack, and clean remove/shutdown without leaked PCS objects. Negative tests should cover reset timeouts, absent platform resources, missing MDIO/PCS devices, unused ports, and register access failures.
