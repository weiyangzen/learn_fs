# Research: subset-b-004319

Grouped research for the DSA switch driver files listed in work item `subset-b-004319`. Each section preserves the source path and is bounded by the reconciliation markers used to split the report into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lan9303-core.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/lan9303-core.c

## Purpose
This is the bus-independent DSA core for SMSC/Microchip LAN9303-family three-port Ethernet switches, including LAN9354 acceptance in the chip-id check. It owns switch discovery, reset sequencing, indirect switch-register access, indirect PHY access for buses that need it, DSA switch registration, special LAN9303 tag setup, bridge separation, FDB/MDB programming, STP state handling, MIB statistics, and phylink MAC behavior.

## Important APIs, Types, and Functions
The file exports `lan9303_register_set`, `lan9303_indirect_phy_ops`, `lan9303_probe()`, `lan9303_remove()`, and `lan9303_shutdown()` for the I2C and MDIO front-ends. Its internal register access helpers are `lan9303_read()`, `lan9303_read_wait()`, `lan9303_write_switch_reg()`, `lan9303_read_switch_reg()`, and masked/port variants. PHY paths are split between virtual PHY port 0 access and `chip->ops` access for physical ports 1 and 2. `lan9303_switch_ops` wires the driver into DSA for tag protocol, setup, ethtool stats, PHY read/write, bridge/FDB/MDB/STP, and port enable/disable.

## Control Flow
Probe initializes mutexes, acquires the optional reset GPIO, toggles reset, performs a byte-order dummy read, waits for `HW_CFG_READY`, validates the chip ID, disables forwarding on user ports, detects PHY address strapping, then registers a three-port DSA switch. DSA setup requires port 0 to be the CPU port, clears virtual PHY Turbo MII mode, configures special VLAN tagging, separates ports 1 and 2 by default, enables the CPU port, and traps IGMP toward port 0. Bridge join switches to bridged mode only once both user ports are in the same bridge; bridge leave restores separation.

## State and Persistence
Persistent runtime state lives in `struct lan9303`: `phy_addr_base`, `is_bridged`, cached `swe_port_state`, reset GPIO data, `indirect_mutex`, `alr_mutex`, and an in-memory ALR cache for static entries. Hardware state is programmed into ALR, VLAN/tagging, mirror, port-state, MIB, and MAC configuration registers and is not persisted across reset. Static FDB/MDB programming is mirrored in `alr_cache`; learned entries are manipulated by walking the hardware ALR.

## Dependencies and Integration Points
The driver depends on Linux DSA, phylink, regmap, GPIO descriptors, OF, MII/PHY helpers, bridge/VLAN headers, and the LAN9303 tagger (`DSA_TAG_PROTO_LAN9303`). Bus-specific code must supply `chip->regmap`, `chip->dev`, and `chip->ops`. It integrates with ethtool statistics through named MIB counters, switchdev FDB/MDB callbacks, bridge STP state changes, VLAN helper calls on the conduit, and optional reset GPIO properties.

## Risks and Test Signals
Important risks are indirect register timeout handling, I2C EEPROM-loader arbitration delays, ALR cache divergence from hardware, unsupported VLAN-aware MDB use (`vid` rejected), assumptions that port 0 is the CPU port, and limited chip-id acceptance despite more LAN935x IDs being defined. Test signals include successful DSA registration, port 0 CPU-port validation, correct no-forwarding default between ports 1 and 2, bridge join/leave traffic behavior, FDB/MDB add/delete/dump, STP transitions, PHY address strap detection for 0-1-2 and 1-2-3 layouts, ethtool stats reads, and phylink speed/duplex/pause configuration on the xMII CPU port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lan9303-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lan9303.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/lan9303.h

## Purpose
This internal header defines the interface between LAN9303 bus front-ends and the shared LAN9303 DSA core. It keeps the transport modules small while centralizing switch behavior in `lan9303-core.c`.

## Important APIs, Types, and Functions
It includes regmap/device/DSA headers plus the public `linux/dsa/lan9303.h` structure definitions. It declares `lan9303_register_set`, `lan9303_indirect_phy_ops`, and lifecycle functions `lan9303_probe()`, `lan9303_remove()`, and `lan9303_shutdown()`.

## Control Flow
There is no runtime control flow in this file. It establishes compile-time linkage: transport drivers allocate/fill `struct lan9303`, create a regmap, choose PHY ops, then call into the declared lifecycle functions.

## State and Persistence
The header owns no state. It exposes shared symbols that operate on caller-owned `struct lan9303` instances.

## Dependencies and Integration Points
The main integration points are the I2C and MDIO modules in the same directory, kernel regmap, and DSA. Any new LAN9303 transport would include this header and provide the same `struct lan9303` fields before invoking `lan9303_probe()`.

## Risks and Test Signals
The header is small, so risks are ABI-style coupling risks: changing declarations or included public headers can break both transport modules. Build coverage with both `lan9303_i2c` and `lan9303_mdio` enabled is the primary test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lan9303.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lan9303_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/lan9303_i2c.c

## Purpose
This is the I2C transport wrapper for LAN9303 managed-mode switches. It provides a regmap over I2C, sets up indirect PHY access, and delegates all switch behavior to the shared LAN9303 core.

## Important APIs, Types, and Functions
`struct lan9303_i2c` embeds the `i2c_client` and shared `struct lan9303`. `lan9303_i2c_regmap_config` defines 8-bit register addresses, 32-bit little-endian values, no cache, and read/write/volatile access tables from `lan9303_register_set`. `lan9303_i2c_probe()`, `lan9303_i2c_remove()`, and `lan9303_i2c_shutdown()` are wired through `module_i2c_driver()`.

## Control Flow
Probe allocates the wrapper, initializes the I2C regmap, stores clientdata, assigns `chip.dev`, selects `lan9303_indirect_phy_ops`, and calls `lan9303_probe()` with the OF node. Remove and shutdown recover the wrapper and call the shared remove/shutdown helpers; shutdown also clears clientdata.

## State and Persistence
The wrapper state is devm-managed and tied to the I2C client lifetime. The regmap is uncached, so all switch state persists only in hardware and shared-core fields.

## Dependencies and Integration Points
The module depends on I2C, OF matching, regmap I2C, and the shared LAN9303 core. Device-tree binding is `"smsc,lan9303-i2c"`, and the legacy I2C id is `"lan9303"`.

## Risks and Test Signals
The main risks are I2C access failures during reset/EEPROM loading, endian or register-width mismatches, and relying on indirect PHY ops for both user PHYs. Test signals include regmap initialization, successful shared probe, correct OF/I2C matching, clean unload/removal, and shutdown without stale clientdata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lan9303_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lan9303_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/lan9303_mdio.c

## Purpose
This is the MDIO transport wrapper for LAN9303/LAN9354 managed-mode switches. It maps 32-bit LAN9303 registers onto pairs of 16-bit MDIO accesses and provides direct nested MDIO PHY read/write operations to the shared LAN9303 core.

## Important APIs, Types, and Functions
`PHY_ADDR()` and `PHY_REG()` translate the LAN9303 register offset into MDIO PHY/register fields. `lan9303_mdio_read()` and `lan9303_mdio_write()` are custom regmap callbacks that lock `mdio_lock` nested and assemble/disassemble 32-bit values. `lan9303_mdio_phy_read()` and `_write()` use nested mdiobus helpers. `lan9303_mdio_probe()`, remove, and shutdown are registered as an `mdio_driver`.

## Control Flow
Probe allocates the wrapper, creates a custom regmap with the shared access table and MDIO callbacks, stores drvdata, assigns `chip.dev`, selects direct MDIO PHY ops, then invokes `lan9303_probe()`. Remove and shutdown hand off to the shared lifecycle helpers and clear drvdata on shutdown.

## State and Persistence
The wrapper stores the `mdio_device` and shared chip object. `smdio`-style paging is not used here; every access is derived from the requested regmap address. All switch configuration state remains in hardware and the core structure.

## Dependencies and Integration Points
The module depends on MDIO device infrastructure, PHY/mdiobus helpers, nested MDIO locking, regmap with custom callbacks, and the LAN9303 core. OF matches include `"smsc,lan9303-mdio"` and `"microchip,lan9354-mdio"`.

## Risks and Test Signals
Risks include 32-bit access tearing if locking is wrong, bad PHY/reg translation, no error handling in low-level `mdio->bus->read/write` helpers beyond returning values, and nested-lock misuse. Test signals include register reads matching the byte-order/chip-id probe, PHY reads on ports 1 and 2, no lockdep warnings, and successful LAN9303 and LAN9354 device-tree matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lan9303_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/Kconfig

## Purpose
This Kconfig fragment defines build-time options for the Lantiq/Intel/MaxLinear GSWIP DSA drivers and their shared common module.

## Important APIs, Types, and Functions
It declares hidden `NET_DSA_LANTIQ_COMMON`, visible `NET_DSA_LANTIQ_GSWIP`, and visible `NET_DSA_MXL_GSW1XX`. The visible options select their tag protocols and the common implementation; the MaxLinear option also selects `PHY_COMMON_PROPS`.

## Control Flow
There is no runtime control flow. Configuration selection determines which objects are built and which DSA taggers/support helpers are pulled in.

## State and Persistence
No runtime state exists. The persistent effect is the kernel configuration state used by Kbuild.

## Dependencies and Integration Points
`NET_DSA_LANTIQ_GSWIP` depends on `HAS_IOMEM` for MMIO SoC switch instances. Both visible drivers select `NET_DSA_LANTIQ_COMMON`; GSWIP selects `NET_DSA_TAG_GSWIP`, while GSW1xx selects `NET_DSA_TAG_MXL_GSW1XX`.

## Risks and Test Signals
Risks are missing dependencies or tagger selections that cause link/build failures. Test signals are `oldconfig` visibility, modular and built-in builds for both drivers, and successful object linkage with the common module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/Makefile

## Purpose
This Makefile maps Lantiq/MaxLinear DSA Kconfig symbols to their object files.

## Important APIs, Types, and Functions
It builds `lantiq_gswip.o` for `CONFIG_NET_DSA_LANTIQ_GSWIP`, `lantiq_gswip_common.o` for `CONFIG_NET_DSA_LANTIQ_COMMON`, and `mxl-gsw1xx.o` for `CONFIG_NET_DSA_MXL_GSW1XX`.

## Control Flow
There is no runtime flow. Kbuild includes objects according to selected configuration symbols.

## State and Persistence
No runtime state. The build graph is the only persistent effect.

## Dependencies and Integration Points
The object mapping aligns with Kconfig: both chip drivers depend on common code, which exports `gswip_probe_common()`.

## Risks and Test Signals
Risks include object naming drift and missing common object linkage when a visible driver is enabled. Test with all three relevant symbols as modules and built-ins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/lantiq_gswip.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/lantiq_gswip.c

## Purpose
This is the SoC MMIO front-end for Lantiq/Intel GSWIP switches in VRX200, xRX300, and xRX330 SoCs. It maps switch/MDIO/MII register windows, validates hardware version and compatible strings, loads internal GPHY firmware when present, and delegates DSA behavior to the common GSWIP implementation.

## Important APIs, Types, and Functions
`struct xway_gphy_match_data` maps SoC revisions to FE/GE firmware names. `gswip_gphy_fw_load()`, `_probe()`, `_remove()`, and `_list()` manage GPHY clocks, resets, firmware DMA allocation, RCU firmware-pointer programming, and settle delays. `gswip_probe()` initializes three MMIO regmaps and calls `gswip_probe_common()`. The `gswip_xrx200` and `gswip_xrx300` `gswip_hw_info` structures define port counts, CPU-port mask, MII/PCDU registers, phylink caps, PCE microcode, and tag protocol.

## Control Flow
Platform probe allocates private state, ioremaps switch/MDIO/MII resources, creates regmaps, obtains match data, reads `GSWIP_VERSION`, checks version-compatible consistency, optionally loads GPHY firmware from the `lantiq,gphy-fw` child, calls the common probe, and stores drvdata. Error paths unload any loaded GPHY firmware. Remove unregisters the DSA switch and tears down GPHY firmware; shutdown calls `dsa_switch_shutdown()`.

## State and Persistence
Runtime state includes mapped regmaps, chosen `hw_info`, RCU regmap, firmware descriptors, and DSA/private common state. GPHY firmware is copied into devm coherent memory aligned to 16 KiB and its DMA address is written to RCU registers until removal resets the pointer. Hardware switch configuration is recreated on probe/setup.

## Dependencies and Integration Points
The driver depends on platform resources, regmap MMIO, syscon RCU phandles, clock/reset APIs, firmware loading, OF child nodes, Lantiq GPHY DT bindings, and `lantiq_gswip_common.c`. It declares firmware names through `MODULE_FIRMWARE()`.

## Risks and Test Signals
Risks include firmware-name/version mismatches, missing reset/clock resources, DMA alignment issues, fixed delays required for PHY availability, and rejecting valid devices if version-compatible checks drift. Test signals include firmware request success, RCU pointer programming, MDIO visibility after the 300 ms delay, correct phylink capabilities per SoC/port, and DSA registration with only CPU port 6 accepted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/lantiq_gswip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/lantiq_gswip.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/lantiq_gswip.h

## Purpose
This shared header defines GSWIP register addresses, bitfields, constants, hardware descriptors, and private state used by both the SoC GSWIP front-end and MaxLinear GSW1xx front-end.

## Important APIs, Types, and Functions
Key types include `struct gswip_pce_microcode`, `struct gswip_hw_info`, `struct gswip_gphy_fw`, `struct gswip_vlan`, and `struct gswip_priv`. The header declares `gswip_probe_common()`. Register groups cover MDIO, MII/PCDU, software reset/version, buffer management/RMON, PCE table access, VLAN/bridge tables, MAC controls, FDMA/SDMA, and GSWIP version comparison helpers.

## Control Flow
There is no executable flow, but its descriptor fields drive runtime behavior: maximum ports, allowed CPU ports, per-port MII/PCDU register presence, 2.5G support, parser microcode pointer, tag protocol, phylink caps, PCS selection, and optional per-port setup callback.

## State and Persistence
`struct gswip_priv` holds all common runtime state: regmaps, hardware info, DSA switch pointer, device pointer, optional RCU firmware mapping, a 64-entry VLAN shadow table, GPHY firmware descriptors, PCE table mutex, and normalized version. The VLAN shadow table is critical because DSA bridge/VLAN operations must be translated into limited hardware table slots.

## Dependencies and Integration Points
It integrates with Linux bitfield helpers, clocks, resets, phylink, platform devices, regmap, mutexes, and DSA. It is included by `lantiq_gswip.c`, `lantiq_gswip_common.c`, PCE microcode headers, and `mxl-gsw1xx.c`.

## Risks and Test Signals
Risks are register-definition drift, incorrect version byte-swapping, mismatched `mii_cfg` sentinel values, and `GSWIP_MAX_PACKET_LENGTH` reflecting a hardware/workaround limit rather than theoretical maximum. Test signals are successful builds for both front-ends, correct field encodings in register writes, and runtime coverage across GSWIP 2.0/2.1/2.2 and GSW1xx descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/lantiq_gswip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/lantiq_gswip_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/lantiq_gswip_common.c

## Purpose
This is the shared DSA implementation for Lantiq/Intel/MaxLinear GSWIP-family switches. It adapts DSA's port, bridge, VLAN, FDB, STP, phylink, MDIO, RMON, EEE, and MTU callbacks to the hardware's PCE/VLAN/MAC/FDMA/SDMA register model.

## Important APIs, Types, and Functions
The private `struct gswip_pce_table_entry` models hardware PCE table transactions. Core helpers include `gswip_pce_table_entry_read/write()`, `gswip_add_single_port_br()`, `gswip_vlan_active_create/remove()`, `gswip_vlan_add/remove()`, `gswip_pce_load_microcode()`, `gswip_mdio()`, and phylink setters for link, speed, duplex, pause, MII mode, and delays. `gswip_switch_ops` exposes DSA callbacks and `gswip_probe_common()` initializes common DSA state and validates the CPU port.

## Control Flow
Common probe initializes the PCE table mutex, allocates and fills `dsa_switch`, normalizes the version, registers with DSA, then validates that exactly one supported CPU port is present. DSA setup resets the switch, disables all ports, initializes VLAN filtering defaults, enables MDIO, loads PCE parser microcode, directs unknown traffic to CPU ports, disables MDIO autopolling, creates the MDIO bus, disables MII interfaces, enables special tagging on CPU ports, enables VLAN-aware switching, flushes the MAC table, and marks ingress MTU enforcement.

## State and Persistence
The driver maintains a 64-entry `priv->vlans` cache mapping bridge devices and VIDs to hardware active-VLAN entries and FIDs. Hardware table state is protected by `pce_table_lock`. Port state is persisted in switch registers until reset; the software VLAN cache must remain consistent with PCE table writes. RMON counters are read from buffer-management RAM, and MIB state remains in hardware counters.

## Dependencies and Integration Points
It depends on DSA, switchdev bridge/VLAN/FDB data, phylink, OF MDIO registration, regmap polling, MII/PHY helpers, and `lantiq_gswip.h` hardware descriptors supplied by chip front-ends. It uses DSA helpers for CPU/user port maps, bridge device lookup, HSR simple join/leave, conduit VLAN handling, and phylink-to-port lookup.

## Risks and Test Signals
High-risk areas are the translation between DSA's VLAN model and the hardware's active-VLAN/FID tables, limited 64-entry VLAN capacity, version-specific learning support, MAC table iteration over 2048 entries, CPU-port validation after DSA registration, and the note that GSWIP 2.2 still uses old VID indexing without a specific control bit. Test signals include standalone port isolation, VLAN-aware and VLAN-unaware bridge joins/leaves, PVID updates, VLAN add/delete capacity errors, FDB add/delete/dump per FID, fast aging, STP state transitions, MDIO child bus operation, RMON counter reads, EEE only on supported versions, and MTU limit enforcement around the 2400-byte workaround.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/lantiq_gswip_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/lantiq_pce.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/lantiq_pce.h

## Purpose
This header contains the parser and classification engine microcode table for Lantiq GSWIP devices, extracted from the vendor switch API. The common driver writes this table into the PCE during setup.

## Important APIs, Types, and Functions
It defines parser output-field enums, parser length/type constants, flag enums, the `MC_ENTRY()` packing macro, and static `gswip_pce_microcode[]` data using `struct gswip_pce_microcode` from `lantiq_gswip.h`.

## Control Flow
The file has no functions. Runtime flow is in `gswip_pce_load_microcode()`, which iterates over this array and writes each packed entry into PCE table values before marking microcode valid.

## State and Persistence
The microcode array is static read-only kernel data. Once loaded, equivalent state exists in the switch PCE until reset.

## Dependencies and Integration Points
It depends on `lantiq_gswip.h` for the microcode structure. `lantiq_gswip.c` references it from SoC `gswip_hw_info` descriptors.

## Risks and Test Signals
Risks are opaque vendor-derived constants, parser regressions for VLAN/SNAP/PPPoE/IPv4/IPv6/IGMP traffic, and mismatches with hardware revisions. Test with tagged/untagged VLAN traffic, IPv4/IPv6, PPPoE, IGMP trapping, and bridge forwarding after PCE load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/lantiq_pce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/mxl-gsw1xx.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/mxl-gsw1xx.c

## Purpose
This is the MDIO/SMDIO front-end for standalone Intel/MaxLinear GSW1xx Ethernet switches. It supplies paged SMDIO regmap access, chip identification, SGMII/1000BASE-X/2500BASE-X PCS support, per-chip hardware descriptors, and then reuses the common GSWIP DSA implementation.

## Important APIs, Types, and Functions
`struct gsw1xx_priv` embeds `struct gswip_priv`, MDIO device state, SMDIO base-address cache, regmaps for switch/MDIO/MII/SGMII/GPIO/clock/shell windows, a `phylink_pcs`, delayed work for clearing RANEG, and current TBI interface. Register access is through `gsw1xx_config_smdio_badr()`, `gsw1xx_regmap_read()`, and `_write()`. PCS operations include enable/disable, get_state, config, AN restart, link_up, SGMII PHY reset, and XAUI side writes. Chip descriptors cover GSW12x, GSW140, GSW141, and GSW150 variants.

## Control Flow
MDIO probe allocates state, initializes SMDIO-backed regmaps for all register windows, validates manufacturer and part IDs from shell registers, initializes PCS if present, configures GPIO pinmux for MMDIO, reads `GSWIP_VERSION`, initializes delayed work, calls `gswip_probe_common()`, logs the standalone part number, and stores drvdata. Remove/shutdown unregister or shut down DSA and cancel delayed work.

## State and Persistence
The cached `smdio_badr` avoids reprogramming the switch base address until a register falls outside the current window. PCS state is represented by `tbi_interface` and hardware SGMII/TBI registers; delayed work clears RANEG after 10 ms because the bit may not self-clear. Hardware state is lost on reset and rebuilt by probe/setup/PCS configuration.

## Dependencies and Integration Points
The driver depends on MDIO, custom regmap bus callbacks, phylink PCS APIs, DSA, PHY common polarity properties, OF match data, delayed work, and `lantiq_gswip_common.c`. It uses `DSA_TAG_PROTO_MXL_GSW1XX` and the MaxLinear PCE microcode table.

## Risks and Test Signals
Risks include SMDIO base-address window errors, nested MDIO locking, PCS reset disrupting active links, polarity interpretation, RANEG self-clear erratum, chip descriptor differences for CPU-port masks and 2.5G support, and GSW150's ambiguous RGMII slew-control scope. Test signals include chip ID validation, SMDIO register reads across page boundaries, DSA registration for each compatible, SGMII/1000BASE-X/2500BASE-X link-up with and without in-band AN, delayed RANEG clear behavior, RMII/RGMII slew DT properties, and common bridge/VLAN/FDB tests through the MaxLinear tagger.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/mxl-gsw1xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/mxl-gsw1xx.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/mxl-gsw1xx.h

## Purpose
This header defines register addresses and bitfields specific to standalone MaxLinear GSW1xx switches, especially SMDIO, SGMII PCS/PHY/TBI, GPIO pinmux, shell identification, RGMII slew, and SGMII clock controls.

## Important APIs, Types, and Functions
It provides constants for port counts and special ports (`GSW1XX_MII_PORT`, `GSW1XX_SGMII_PORT`), SMDIO base-address control, SGMII TBI autonegotiation/link-partner status, internal SGMII PHY access, PCS buffer resets, polarity/equalization/boost settings, switch/register-window bases, GPIO alternate-select values, shell manufacturer/part-number fields, RGMII slew bits, and SGMII clock NCO settings.

## Control Flow
There is no executable flow. These definitions drive register operations in `mxl-gsw1xx.c`, especially regmap window construction, chip ID validation, PCS reset/configuration, and 1G versus 2.5G clock selection.

## State and Persistence
No software state is defined here. Hardware state addressed by these constants persists in the chip until reset or driver reconfiguration.

## Dependencies and Integration Points
The header depends on `linux/bitfield.h` and is consumed by the MaxLinear front-end. It complements generic GSWIP definitions in `lantiq_gswip.h`.

## Risks and Test Signals
Risks are incorrect register offsets or bitfield masks, especially for PCS and shell ID logic. Test signals include successful ID extraction, SGMII/1000BASE-X/2500BASE-X negotiation, clock switching, polarity settings, and GPIO MMDIO pinmux behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/mxl-gsw1xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/mxl-gsw1xx_pce.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/mxl-gsw1xx_pce.h

## Purpose
This header contains the MaxLinear GSW1xx parser/classification microcode used by the common GSWIP setup path. Compared with the older Lantiq table, it includes updated handling for service VLAN tags and an IPv6 issue fix noted in comments.

## Important APIs, Types, and Functions
It defines parser output enums including `OUT_STAG0/OUT_STAG1`, parser type constants, flag enums including `FLAG_SVLAN`, a `PCE_MC_M()` packing macro, and static `gsw1xx_pce_microcode[]` entries of `struct gswip_pce_microcode`.

## Control Flow
No functions execute in this header. `mxl-gsw1xx.c` points `gswip_hw_info.pce_microcode` at this array, and `gswip_pce_load_microcode()` writes it during DSA setup.

## State and Persistence
The array is read-only kernel data. The loaded parser table becomes hardware PCE state until reset.

## Dependencies and Integration Points
It includes `lantiq_gswip.h` for the shared microcode structure and is integrated by all GSW1xx `gswip_hw_info` descriptors.

## Risks and Test Signals
Risks are opaque microcode constants and parser behavior regressions for stacked VLAN, IPv6 extension headers, PPPoE, SNAP, and IGMP. Test signals should cover S-tag/C-tag traffic, IPv6 forwarding, IGMP trapping, VLAN-aware bridging, and comparison with vendor-documented parser behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/mxl-gsw1xx_pce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/Kconfig

## Purpose
This Kconfig fragment defines Microchip KSZ DSA driver options, including the shared KSZ switch core, transport drivers, optional PTP support, and the KSZ8863 SMI transport.

## Important APIs, Types, and Functions
`NET_DSA_MICROCHIP_KSZ_COMMON` is a menuconfig for the common switch support and selects DSA taggers, IEEE 802.1Q helpers, DCB, and XPCS. Transport options are `NET_DSA_MICROCHIP_KSZ9477_I2C`, `NET_DSA_MICROCHIP_KSZ_SPI`, and `NET_DSA_MICROCHIP_KSZ8863_SMI`. `NET_DSA_MICROCHIP_KSZ_PTP` gates timestamp/PTP support for supported newer chips.

## Control Flow
No runtime flow exists. Configuration controls which common and bus-specific objects are built and which dependencies are selected.

## State and Persistence
No runtime state. The kernel configuration persists build choices.

## Dependencies and Integration Points
The common option depends on `NET_DSA`; I2C and SPI transports depend on their bus frameworks and select matching regmap buses; SMI selects `MDIO_BITBANG`. PTP depends on `PTP_1588_CLOCK` with built-in/module consistency constraints.

## Risks and Test Signals
Risks include broad common option text covering chips not in this subset, dependency omissions, and module/built-in PTP dependency mistakes. Test signals include all transport combinations in `allmodconfig`-style builds and correct menu visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/Makefile

## Purpose
This Makefile composes the Microchip KSZ DSA common module and transport modules from Kconfig selections.

## Important APIs, Types, and Functions
`ksz_switch.o` is built for `CONFIG_NET_DSA_MICROCHIP_KSZ_COMMON` from common, DCB, KSZ9477, ACL, flower, KSZ8, and LAN937x objects. `ksz_ptp.o` is conditionally added when PTP is enabled. Separate modules are built for I2C, SPI, and KSZ8863 SMI transports.

## Control Flow
No runtime control flow. Kbuild uses the object list to link feature families into the shared `ksz_switch` module and separate bus entry points.

## State and Persistence
No runtime state. Persistent effect is the object dependency graph.

## Dependencies and Integration Points
The KSZ8 implementation researched here is linked into the common module, while `ksz8863_smi.o` is its own transport that registers a `ksz_device` with the common switch framework.

## Risks and Test Signals
Risks are missing objects in the composite module or conditional PTP link errors. Test by building common-only, SMI, I2C, SPI, and PTP-enabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz8.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz8.c

## Purpose
This is the KSZ8-family switch implementation used by the Microchip KSZ common DSA core. It supports KSZ8463, KSZ8863/8873, KSZ8895/8864, and KSZ8794/8795/8765 style devices with PHY emulation, VLAN/FDB/MDB tables, MIB counters, port setup, mirroring, MTU changes, errata handling, CPU-port configuration, and phylink link-up programming.

## Important APIs, Types, and Functions
The file exports the operations declared in `ksz8.h`, including setup, switch init/exit, reset, port address helpers, PHY read/write, MIB reads, FDB/MDB add/delete/dump, VLAN filtering/add/delete, mirror add/delete, CPU-port setup, phylink link-up, MTU change, PME indirect access, and queue split. Important internal helpers are `ksz8_ind_read8/write8()`, `ksz8_r_table/w_table()`, dynamic/static MAC table readers/writers, VLAN encode/decode/read/write helpers, PHY BMCR/control translation, and chip-family-specific MTU and MIB packet readers.

## Control Flow
Switch setup marks ingress MTU enforcement and software untagging behavior, enables link auto-aging and half-duplex backoff, programs default VLAN/mirror/tag behavior, loads the VLAN cache from hardware, disables PME/interrupts where applicable, and applies the KSZ87xx EEE erratum. Port setup enables storm limiting, queue split, priority behavior, membership maps, and disables WoL options by default. CPU-port configuration enables tail tagging, sets up the CPU port, handles legacy interface selection/RMII clock mode, disables user ports through STP, detects fiber mode, and disables unsupported KSZ8463 PTP behavior.

## State and Persistence
State spans `struct ksz_device`, per-port state, VLAN cache, MIB counters, mirror bitmaps, ALU mutex protection, and hardware tables. Static MAC entries persist in hardware static tables; dynamic entries are read by indexed hardware iteration. VLAN cache mirrors hardware VLAN table entries to support DSA operations and untag/PVID decisions. Dropped-packet counters for some chips use software delta tracking because hardware exposes wrapping packet-dropped counters.

## Dependencies and Integration Points
The driver depends on the KSZ common framework (`ksz_common.h` helpers and chip data), DSA, switchdev, phylink, bridge/VLAN flags, Micrel PHY definitions, regmap accessors, and chip-specific masks/shifts/register arrays from common data. It is linked into `ksz_switch.o` and called through the common KSZ operation tables.

## Risks and Test Signals
High-risk areas include per-chip register differences, PHY register emulation bit inversions between KSZ879x and KSZ8873, VLAN filtering unsupported on KSZ88x3/KSZ8463, single remove-tag behavior limiting mixed tagged/untagged VLANs, static table capacity, FID equals VID simplification, MIB valid/overflow handling, and unsupported asymmetric pause forcing. Test signals include PHY read/write emulation for BMCR/BMSR/advertise/LPA/link-md/control, VLAN add/delete and PVID behavior, FDB/MDB table capacity and deletion, dynamic FDB dump, MIB counter increments/overflow, mirror ingress/egress configuration, CPU tail tagging, STP disable/forward transitions via common code, MTU changes per chip family, and KSZ87xx EEE erratum register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz8.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz8.h

## Purpose
This internal header declares the KSZ8-family operation surface used by the Microchip KSZ common switch core and by transport-specific code.

## Important APIs, Types, and Functions
It declares setup, port address, port membership, dynamic MAC flush, port setup, PHY access, MIB access, FDB/MDB operations, VLAN operations, mirroring, phylink caps/link-up, CPU port configuration, STP address programming, reset/init/exit, MTU change, PME access, queue split, and KSZ8463-specific port/PHY helpers.

## Control Flow
There is no runtime control flow. The declarations allow `ksz_common` chip operation tables and transports to call into `ksz8.c` implementations.

## State and Persistence
No state is declared directly. All functions operate on `struct ksz_device`, `struct dsa_switch`, or phylink/switchdev objects owned elsewhere.

## Dependencies and Integration Points
The header includes `ksz_common.h`, DSA types, and Linux integer types. It is the compile-time contract between KSZ8-specific code and the shared KSZ framework.

## Risks and Test Signals
Risks are signature drift against operation-table expectations and missing declarations for newly implemented KSZ8 hooks. Build coverage with all KSZ8 transports and common code is the key signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz8863_smi.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz8863_smi.c

## Purpose
This is the SMI-over-MDIO transport driver for Microchip KSZ8863 and KSZ8873 switches. It presents 8/16/32-bit regmaps to the common KSZ switch framework using the chip's custom SMI frame encoding.

## Important APIs, Types, and Functions
`ksz8863_mdio_read()` and `ksz8863_mdio_write()` implement regmap bus access through locked raw mdiobus reads/writes. The `regmap_smi` array supplies buses for 8-, 16-, and 32-bit access, with big-endian defaults for wider values. `ksz8863_regmap_config` defines address/value widths, no cache, common KSZ regmap locking, and `U8_MAX` register range. Probe allocates `ksz_device`, initializes all regmaps with chip access tables, then calls `ksz_switch_register()`.

## Control Flow
MDIO probe gets match-data chip definition, creates the three regmaps, copies platform data if present, registers the switch with the common KSZ core, and stores drvdata. Remove calls `ksz_switch_remove()`. Shutdown calls `dsa_switch_shutdown()` and clears drvdata.

## State and Persistence
Transport state is stored in the `ksz_device` allocated by `ksz_switch_alloc()`, with `dev->priv` pointing at the MDIO device. Regmaps are uncached; hardware registers are the source of truth. MDIO bus access is serialized through nested `mdio_lock`.

## Dependencies and Integration Points
The driver depends on MDIO, regmap custom buses, the KSZ common framework, match data from `ksz_switch_chips[KSZ88X3]`, and OF compatibles `"microchip,ksz8863"` and `"microchip,ksz8873"`.

## Risks and Test Signals
Risks include SMI frame address encoding errors, pointer arithmetic on regmap write buffers, endianness for 16/32-bit access, lock nesting, and failed deferred registration when the main DSA core is not ready. Test signals include regmap reads/writes across register ranges, chip detection through common probe, no lockdep warnings, remove/shutdown cleanup, and working KSZ8 PHY/VLAN/FDB callbacks over this transport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz8863_smi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz8_reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz8_reg.h

## Purpose
This header defines register addresses, bit masks, table encodings, PHY-emulation constants, MIB constants, ACL/PME/EEE indirect access fields, and chip IDs for KSZ8-family switches.

## Important APIs, Types, and Functions
It covers global switch controls, power management, per-port controls/status, PHY/link-md registers, indirect table selection, interrupt registers, VLAN/static/dynamic/MIB table layouts, PME and ACL register fields, chip IDs for KSZ8795 and KSZ8863 families, KSZ8463-specific PHY/PTP/configuration registers, queue and priority constants, common alias names used by the driver, tail-tag bits, FID/table sizes, and MIB masks.

## Control Flow
There is no executable flow. `ksz8.c` and common chip data use these definitions to construct register reads/writes and interpret table data.

## State and Persistence
The header owns no software state. It names hardware state locations that persist in the switch until reset, including VLAN/ALU tables, MIB counters, power management, and per-port PHY control/status.

## Dependencies and Integration Points
It is included by `ksz8.c` and works with chip-specific masks/shifts/register arrays from `ksz_common`. It provides common aliases so KSZ8 code can share helper logic across chip variants.

## Risks and Test Signals
Risks include duplicated/overlapping register definitions across variants, alias constants hiding chip-specific differences, a suspicious self-referential `TABLE_LINK_MD` definition, and bit inversions that must match each chip family. Test signals include compile-time use by all KSZ8 chip data, register-level smoke tests on KSZ88x3/KSZ87xx/KSZ8463, VLAN/FDB/MIB table correctness, PHY register emulation, and PME/ACL indirect access where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz8_reg.h -->
