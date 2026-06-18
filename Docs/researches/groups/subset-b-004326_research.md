# Research Report: subset-b-004326

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx.c

## Purpose
This file is the DSA MDIO driver for the MaxLinear MxL862xx switch family. It registers an MDIO-backed `dsa_switch`, wraps the firmware command interface through `mxl862xx_api_wrap()`, sets up the internal PHY MDIO relay, programs bridge and VLAN forwarding resources, implements FDB/MDB/STP/bridge flag callbacks, and exposes ethtool and `rtnl_link_stats64` statistics.

## Important APIs, Types, and Functions
- `MXL862XX_API_READ`, `MXL862XX_API_WRITE`, and `MXL862XX_API_READ_QUIET` are local convenience wrappers over firmware commands defined in the companion API headers.
- `mxl862xx_get_tag_protocol()` always returns `DSA_TAG_PROTO_MXL862`, tying the driver to the MxL862 DSA tagger.
- `mxl862xx_phy_read_mmd()` and `mxl862xx_phy_write_mmd()` implement firmware-relayed internal PHY access and are exposed through the `mii_bus` hooks in `mxl862xx_setup_mdio()`.
- `mxl862xx_wait_ready()` polls firmware version and common config reads after reset.
- `mxl862xx_setup()` performs firmware reset/readiness, calculates per-port EVLAN/VLAN-filter table budgets, installs the shared drop meter, starts stats polling, and registers the internal MDIO bus.
- `mxl862xx_port_setup()` disables and flushes a port, configures service-port tagging and CTP assignment, creates standalone bridge/FID state for user ports, and allocates per-port ingress EVLAN, egress EVLAN, and VLAN Filter blocks.
- VLAN handling is split among `mxl862xx_vf_*()` helpers for membership filtering, `mxl862xx_evlan_*()` helpers for tag insertion/removal/PVID behavior, and DSA callbacks `mxl862xx_port_vlan_filtering()`, `mxl862xx_port_vlan_add()`, and `mxl862xx_port_vlan_del()`.
- Bridge behavior is implemented by `mxl862xx_allocate_bridge()`, `mxl862xx_free_bridge()`, `mxl862xx_sync_bridge_members()`, `mxl862xx_set_bridge_port()`, `mxl862xx_port_bridge_join()`, and `mxl862xx_port_bridge_leave()`.
- FDB and MDB callbacks program firmware MAC table entries through `MXL862XX_MAC_TABLEENTRY*` commands.
- Statistics come from `mxl862xx_read_rmon()`, ethtool callbacks, periodic `mxl862xx_stats_poll()`, and `mxl862xx_get_stats64()`.
- Driver lifecycle is `mxl862xx_probe()`, `mxl862xx_remove()`, `mxl862xx_shutdown()`, and the `mdio_driver`/OF match table.

## Control Flow
Probe allocates `mxl862xx_priv` and `dsa_switch`, initializes host transport state with `mxl862xx_host_init()`, initializes per-port work and stats locks, and calls `dsa_register_switch()`. DSA then calls `mxl862xx_setup()`, which resets the chip, waits for firmware, sizes hardware VLAN resources based on user-port count, sets up a zero-rate drop meter, starts delayed stats polling, and registers the child MDIO bus.

Per-port setup first disables DMA paths and flushes MAC learning. CPU ports enable service-port tagging and are assigned to the default bridge. User ports get an individual firmware bridge for standalone operation, initially block unknown unicast/multicast host flooding while allowing broadcast, then allocate ingress EVLAN, egress EVLAN, and VLAN Filter blocks.

Bridge join allocates one firmware bridge per DSA bridge number if needed, then reprograms all current bridge members. `mxl862xx_set_bridge_port()` is the main convergence point: it builds the bridge port map, assigns the correct bridge/FID, applies learning and flood-block meter state, enables EVLAN/VF blocks when applicable, and switches between IVL/SVL by setting VLAN-based MAC learning flags.

VLAN-aware ingress uses fixed final EVLAN rules that insert the PVID for untagged/priority-tagged traffic, pass standard 802.1Q VID>0 traffic to VLAN Filter membership checks, and treats non-802.1Q TPIDs as untagged. Egress EVLAN rules are created only for untagged VIDs that need tag stripping. VLAN Filter entries track allowed VIDs per port and use a discard sentinel at index 0 when the active scan window would otherwise be empty.

Remove and shutdown stop delayed stats work, unregister or shut down DSA, shut down the host transport, and cancel deferred host-flood work. Port teardown only marks `setup_done = false`; EVLAN/VF firmware resources are reclaimed by firmware reset on next probe rather than freed individually.

## State and Persistence Behavior
The driver persists runtime state in `struct mxl862xx_priv` and `struct mxl862xx_port`. Per-port state includes standalone FID, flood-block bitmask, learning flag, setup guard, PVID, VLAN filtering mode, allocated VF/EVLAN block IDs, desired host flooding, deferred work, and accumulated stats. Bridge IDs are cached in `priv->bridges[]` by DSA bridge number. Hardware tables and meters persist in firmware until reset; software does not reconstruct them from persistent storage.

Stats are accumulated in software because RMON packet counters are 32-bit free-running values. `mxl862xx_stats_poll()` computes deltas against previous snapshots, handles 32-bit wrap with unsigned subtraction, and stores 64-bit accumulators under `stats_lock`. `MXL862XX_FLAG_WORK_STOPPED` prevents delayed work rescheduling during teardown.

Host flood changes are special because DSA may call `port_set_host_flood` under `netif_addr_lock`. The driver records the desired state and schedules `host_flood_work`, which takes RTNL, verifies `setup_done`, and writes firmware bridge forwarding configuration for the standalone FID.

## Dependencies and Integration Points
The file depends on Linux DSA, phylink, OF MDIO, bridge switchdev flags, ethtool stats APIs, and the companion MxL862xx firmware transport/API headers: `mxl862xx-api.h`, `mxl862xx-cmd.h`, and `mxl862xx-host.h`. It integrates with the DSA tagger via `DSA_TAG_PROTO_MXL862`, with internal PHYs via a child `mdio` node, and with firmware command structures whose fields require explicit CPU/little-endian conversions.

## Risks and Edge Cases
- EVLAN rule order is critical. The standard 802.1Q accept rules must precede broad `NO_FILTER` catchalls or valid tagged frames could be stripped or rewritten.
- VLAN resource sizing divides global EVLAN/VF tables among user ports. Large VLAN deployments can hit `-ENOSPC`, especially for untagged egress VIDs that consume EVLAN entries.
- Rollback after VLAN add/delete errors is best effort. The code restores software state and reprograms blocks, but there is no true firmware transaction.
- The shared zero-rate drop meter relies on direct register modification after firmware allocation to eliminate an initial bucket leak.
- `mxl862xx_vf_del_vid()` swaps the last active VF entry into a removed entry's gap; correctness depends on list/index consistency.
- Host flood work can race with teardown unless `setup_done` and RTNL ordering are preserved.
- FID allocation failures or partial port setup may leak firmware bridges until reset, which the code comments treat as tolerable.
- `mxl862xx_get_stats64()` returns accumulated values and schedules an immediate poll for freshness, so the current call may lag hardware by up to the poll interval.

## Test Signals
Useful test coverage would include module probe/remove/shutdown, child MDIO scan and PHY reads, DSA bridge join/leave with multiple bridges, standalone flooding behavior, bridge flags for learning and unknown UC/MC/broadcast flooding, VLAN-aware and VLAN-unaware traffic with PVID/untagged/tagged combinations, FDB/MDB add/delete/dump, STP state transitions with learning reapplication, RMON wraparound behavior, ethtool stat mapping, and fault injection for firmware command failures during VLAN add/delete rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx.h

## Purpose
This header defines the private data model used by the MxL862xx DSA driver. It centralizes hardware size constants, firmware portmap helpers, per-port VLAN Filter and Extended VLAN bookkeeping, software statistics accumulators, and the top-level `mxl862xx_priv` structure.

## Important APIs, Types, and Functions
- `MXL862XX_MAX_PORTS`, `MXL862XX_MAX_BRIDGES`, `MXL862XX_MAX_BRIDGE_PORTS`, `MXL862XX_TOTAL_EVLAN_ENTRIES`, and `MXL862XX_TOTAL_VF_ENTRIES` define driver sizing assumptions.
- `mxl862xx_fw_portmap_set_bit()`, `mxl862xx_fw_portmap_clear_bit()`, and `mxl862xx_fw_portmap_is_empty()` operate on firmware-format 128-bit portmaps represented as little-endian 16-bit words.
- `struct mxl862xx_vf_vid` tracks a software VID entry in a per-port VLAN Filter block, including hardware index and egress untagged state.
- `struct mxl862xx_vf_block` tracks a hardware VLAN Filter allocation, active scan count, block size, and VID list.
- `struct mxl862xx_evlan_block` tracks Extended VLAN block allocation, enable state, block ID, total size, and active rule count.
- `struct mxl862xx_port_stats` stores 64-bit accumulated link stats plus previous raw hardware snapshots.
- `struct mxl862xx_port` is the per-port runtime object.
- `struct mxl862xx_priv` is the driver-wide object associated with `dsa_switch::priv`.

## Control Flow
The header itself has no control flow beyond inline portmap helpers. Its structures are populated by `mxl862xx_probe()`, `mxl862xx_setup()`, `mxl862xx_port_setup()`, VLAN callbacks, bridge callbacks, stats work, and remove/shutdown paths in `mxl862xx.c`.

## State and Persistence Behavior
All state is runtime-only and rebuilt on probe. `struct mxl862xx_port` records bridge/FID, learning, flood-block, PVID, VLAN filtering, VF/EVLAN allocations, deferred work, and stats per port. `struct mxl862xx_priv` records the MDIO device, DSA switch, CRC/work flags, shared drop meter ID, per-port array, DSA-bridge-to-firmware-bridge mapping, table block sizing, and delayed stats work. No state is persisted outside memory; firmware state is expected to be reset and reallocated during setup.

## Dependencies and Integration Points
The header includes Linux MDIO and workqueue types plus `net/dsa.h`. Its types are tightly coupled to firmware command structures in other MxL862xx headers, particularly because firmware portmaps use little-endian words and VLAN/EVLAN block IDs come from firmware allocation commands.

## Risks and Edge Cases
- Portmap helpers do not bounds-check `port`; callers must keep indexes below `MXL862XX_MAX_BRIDGE_PORTS`.
- Little-endian bit operations require careful use of `cpu_to_le16()` and cannot be safely replaced with native bitmaps.
- `mxl862xx_fw_portmap_is_empty()` checks raw `__le16` words for zero, which is valid for zero but would not be suitable for arbitrary numeric interpretation.
- `setup_done` is used as a concurrency guard for deferred work; any new worker touching per-port state must respect it.
- Stats locking only protects accumulators, not the MDIO reads that produce snapshots.

## Test Signals
Header-level validation is mostly compile-time and behavior driven from `mxl862xx.c`. KUnit-style tests could exercise firmware portmap bit set/clear/empty behavior on little-endian arrays, while integration tests should verify VF/EVLAN allocation state transitions, work cancellation, and stat accumulator locking under polling plus `get_stats64()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/Kconfig

## Purpose
This Kconfig file declares the build-time configuration entries for the Ocelot/Felix DSA driver family. It separates the shared Felix DSA library from chip/front-end drivers for external SPI-controlled Ocelot switches, PCIe Felix/VSC9959, and platform Seville/VSC9953.

## Important APIs, Types, and Functions
- `NET_DSA_MSCC_FELIX_DSA_LIB` is a hidden tristate library selected by the concrete drivers. It builds the common Felix DSA glue in `felix.c`.
- `NET_DSA_MSCC_OCELOT_EXT` enables the SPI/MFD external Ocelot switch front end and selects `MFD_OCELOT`, `MDIO_MSCC_MIIM`, the Ocelot switch library, both Ocelot DSA taggers, and the Felix DSA library.
- `NET_DSA_MSCC_FELIX` enables the PCI VSC9959/NXP LS1028A Felix driver and depends on PCI, Microsemi and Freescale vendor options, MMIO, optional PTP, and taprio availability. It selects the shared switch library, Felix library, Ocelot taggers, ENETC MDIO, and Lynx PCS.
- `NET_DSA_MSCC_SEVILLE` enables the VSC9953 Seville platform driver and selects MDIO, Ocelot switch library, Felix library, Ocelot taggers, and Lynx PCS.

## Control Flow
Kconfig has no runtime control flow. Its dependency and select graph controls which objects are compiled and which helper libraries are pulled in when a user enables a specific Ocelot-compatible switch driver.

## State and Persistence Behavior
Configuration state is held in the kernel build configuration. There is no runtime state. Built-in versus module behavior follows the tristate choices and selected dependencies.

## Dependencies and Integration Points
The entries integrate with DSA, the Microsemi/Ocelot switch library, Ocelot DSA taggers, optional PTP clock support, MDIO providers, PCS Lynx, PCI, SPI, MFD Ocelot, and vendor menu symbols. The Felix driver specifically constrains `NET_SCH_TAPRIO` to either enabled or absent in a way that avoids unsupported modular dependency combinations.

## Risks and Edge Cases
- `select` bypasses dependency prompts for selected symbols, so the dependency list must remain accurate for each hardware front end.
- `NET_DSA_MSCC_FELIX_DSA_LIB` is hidden; it should not gain direct user-facing hardware assumptions.
- The taprio dependency for `NET_DSA_MSCC_FELIX` is subtle and important for TSN offloads.
- External Ocelot support is described as SPI-controlled and depends on `MFD_OCELOT`; mismatched device tree/MFD setup will prevent runtime probe even if Kconfig succeeds.

## Test Signals
Build tests should cover all three concrete options as built-in and module where supported, with combinations of `PTP_1588_CLOCK_OPTIONAL` and `NET_SCH_TAPRIO`. Runtime smoke tests should verify that enabling each option builds the expected object and pulls in the correct DSA tagger modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/Makefile

## Purpose
This Makefile maps Ocelot/Felix Kconfig symbols to kernel objects and declares the object composition for each module.

## Important APIs, Types, and Functions
- `mscc_felix_dsa_lib.o` is built when `CONFIG_NET_DSA_MSCC_FELIX_DSA_LIB` is enabled and contains `felix.o`.
- `mscc_felix.o` is built for `CONFIG_NET_DSA_MSCC_FELIX` and contains `felix_vsc9959.o`.
- `mscc_ocelot_ext.o` is built for `CONFIG_NET_DSA_MSCC_OCELOT_EXT` and contains `ocelot_ext.o`.
- `mscc_seville.o` is built for `CONFIG_NET_DSA_MSCC_SEVILLE` and contains `seville_vsc9953.o`.

## Control Flow
There is no runtime control flow. Kbuild reads these mappings to compile the shared library and the selected front-end modules.

## State and Persistence Behavior
The only state is build metadata. The file does not store runtime state or generated artifacts.

## Dependencies and Integration Points
This file must stay consistent with `Kconfig` symbols and with exported symbols from `felix.c`, especially `felix_register_switch()`, `felix_port_to_netdev()`, and `felix_netdev_to_port()`, which are used by the front-end modules.

## Risks and Edge Cases
- If a Kconfig symbol is renamed without updating this Makefile, the corresponding driver silently stops building.
- The shared library must be selected by every front-end that calls exported Felix helpers.
- Object names define module names, so changes may affect module autoloading and packaging.

## Test Signals
Compile each Kconfig option and inspect that the expected modules are produced. A useful static check is to compare Kconfig symbol names against `obj-$(CONFIG_...)` entries and ensure every front-end object links with the shared library when needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/felix.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/felix.c

## Purpose
`felix.c` is the common DSA front end for Ocelot-compatible switches that communicate with the host through an NPI Ethernet CPU port or the software-defined `ocelot-8021q` tag protocol. It converts DSA callbacks into Ocelot switch-library operations, manages tag protocol setup and migration, initializes register maps and ports from `felix_info`, handles timestamping and MMIO packet extraction, and exports registration helpers used by chip-specific drivers.

## Important APIs, Types, and Functions
- `felix_register_switch()` is the exported entry point for chip-specific front ends. It allocates `struct felix` and `dsa_switch`, initializes Ocelot core fields, sets the initial tag protocol, and calls `dsa_register_switch()`.
- `felix_port_to_netdev()` and `felix_netdev_to_port()` are exported adapters used by Ocelot ops for netdev/port translation.
- `felix_classify_db()` maps DSA FDB/MDB database objects to the Ocelot library's bridge-dev convention.
- Tag protocol management is implemented by `felix_change_tag_protocol()`, `felix_connect_tag_protocol()`, `felix_tag_npi_*()`, `felix_tag_8021q_*()`, and shared migration helpers.
- `felix_update_tag_8021q_rx_rule()`, `felix_tag_8021q_vlan_add_rx()`, `felix_tag_8021q_vlan_add_tx()`, and related delete/update helpers program ES0/IS1/IS2 VCAP rules that identify source ports and redirect TX traffic for tag_8021q.
- `felix_update_trapping_destinations()` rewrites trap rules when tag protocol and no-XTR-IRQ behavior require different CPU destinations.
- DSA bridge/FDB/MDB/LAG/VLAN/STP callbacks mostly wrap `ocelot_*` library functions while handling CPU/NPI special cases.
- Phylink callbacks delegate MAC config/link state to the Ocelot library and chip-specific `felix_info` callbacks.
- `felix_init_structs()` parses device tree ports, requests target and per-port regmaps, initializes regfields, creates Ocelot port objects, and optionally allocates the chip MDIO bus.
- `felix_setup()` initializes Ocelot hardware, timestamping, ports, serdes, QoS maps, IRQ, devlink shared buffers, initial tag protocol, and DSA capability flags.
- PTP/timestamping paths include `felix_hwtstamp_get()`, `felix_hwtstamp_set()`, `felix_rxtstamp()`, `felix_txtstamp()`, and `felix_port_deferred_xmit()`.
- Devlink, tc, mirror, policer, MRP, priority, MAC Merge, HSR, stats, and MTU callbacks are mapped through `felix_switch_ops`.

## Control Flow
Chip drivers call `felix_register_switch()` with a hardware-specific `felix_info`. During DSA setup, `felix_setup()` calls `felix_init_structs()` to populate the embedded `struct ocelot`, maps resources from either hardcoded PCI resources or parent MFD regmaps, initializes regfields and port structures, and invokes optional MDIO allocation. It then runs Ocelot initialization, optional PTP setup, per-port initialization, optional serdes setup, QoS map initialization, optional IRQ request, devlink shared-buffer registration, and initial tag protocol setup.

The tag-protocol path has two modes. NPI mode configures the hardware CPU port module through `felix_npi_port_init()`, supports only one active conduit, and forwards host traffic through the NPI PGID. `ocelot-8021q` mode registers the tag_8021q tagger, configures CPU/user port assignments, programs VCAP rules through DSA tag VLAN callbacks, drains the CPU extraction queue, and sets DSA's VLAN-aware PVID untagging workaround. Protocol changes set up the new mode first, migrate MDB and host flood destinations, update trap destinations, then tear down the old mode.

Packet switching callbacks mostly translate DSA object shapes into Ocelot calls. CPU/NPI ports are remapped to `PGID_CPU` or `ocelot->num_phys_ports` where the Ocelot library models CPU-facing resources differently from physical DSA port numbers.

Timestamp receive handling either reconstructs a full timestamp using the low timestamp from the tagger plus the current PTP time, or, when the no-XTR-IRQ workaround is active, discards the Ethernet notification skb and polls the MMIO extraction group for the original trapped PTP frame. TX timestamping records a clone in Ocelot state and deferred tag_8021q injection removes the clone on injection failure.

Teardown reverses tag protocol setup under RTNL, deinitializes ports, unregisters devlink shared buffers, tears down timestamping and Ocelot core state, and frees chip-specific MDIO resources.

## State and Persistence Behavior
`struct felix` stores the `dsa_switch`, hardware info, embedded `struct ocelot`, optional internal MDIO bus and PCS array, switch base address, current tag protocol, current tag protocol ops, TX kthread worker pointer, and host flood masks. The embedded `struct ocelot` stores most hardware state such as ports, regmaps, VCAP blocks, PTP state, forwarding domains, devlink state, stats, and tc offloads. Runtime state is rebuilt on probe and is not persisted across driver unload or hardware reset.

Host flood masks are stored independently of the current tag protocol so they can be reapplied to the proper CPU forwarding mask during tag protocol migration. The tag protocol pointer is updated only after the new protocol and shared resources are successfully configured.

## Dependencies and Integration Points
The file depends on DSA, DSA taggers `ocelot` and `ocelot-8021q`, the Ocelot switch library and register definitions, phylink, PTP classification and timestamping, devlink shared buffers, switchdev, tc flower/policer/mirror/offload APIs, MRP, HSR helpers, OF parsing, regmap, platform/PCI device abstractions, and chip-specific callbacks supplied through `struct felix_info`.

## Risks and Edge Cases
- `felix_update_tag_8021q_rx_rules()` assumes the ES0 rule exists when VLAN filtering changes; missing rules would lead to a null dereference path if setup sequencing is broken.
- Changing NPI conduit is constrained because user ports still assigned to the old conduit must be down. Violating this would strand traffic.
- No-XTR-IRQ timestamp workaround is delicate: Ethernet packets act as notifications only, while real timestamped frames are extracted over MMIO.
- `felix_mrp_del()` calls `ocelot_mrp_add()` rather than a delete helper, which is a suspicious behavior signal and should be checked against the Ocelot API.
- Many callbacks remap CPU/NPI ports. Off-by-one or stale `ocelot->npi` values can affect FDB/MDB/bridge flag behavior.
- Tag protocol migration is intended to be consistent because NPI setup cannot fail, but new protocol setup and shared migration still need careful rollback.
- `felix_port_deferred_xmit()` frees its work object only on success; the failure branch frees the skb but not `xmit_work`, which is worth auditing against allocation ownership.

## Test Signals
High-value tests include DSA probe/remove for each front end, NPI and `ocelot-8021q` tag protocol setup and live migration, conduit changes with ports up/down and LAG conduits, VLAN filtering toggles under tag_8021q, FDB/MDB on standalone/bridge/LAG/CPU databases, PTP RX/TX timestamping with and without extraction IRQ, tc flower traps and trap destination migration, devlink shared-buffer operations, HSR behavior under each tag protocol, and fault-injection around regmap/MDIO/IRQ/timestamp initialization failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/felix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/felix.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/felix.h

## Purpose
This header defines the public internal interface between the shared Felix DSA library and chip-specific Ocelot-compatible front-end drivers. It declares supported port-mode bitmasks, `struct felix_info` hardware description, tag-protocol operation hooks, `struct felix` runtime state, and exported helper prototypes.

## Important APIs, Types, and Functions
- `ocelot_to_felix()` converts an embedded `struct ocelot *` back to `struct felix *`.
- `FELIX_MAC_QUIRKS` currently aliases `OCELOT_QUIRK_PCS_PERFORMS_RATE_ADAPTATION`.
- `OCELOT_PORT_MODE_*` bitmasks describe allowed PHY interface modes per port.
- `struct felix_info` is the chip profile consumed by `felix_register_switch()`. It contains resource tables, target names, regfields, register maps, Ocelot ops, port modes, MAC table and VCAP capacities, PTP caps, quirks, and optional callbacks for MDIO, tc, scheduler speed, MAC config, serdes, and IRQ setup.
- `struct felix_tag_proto_ops` abstracts setup/teardown and host-forwarding behavior for NPI versus `ocelot-8021q` tag protocols.
- `struct felix` stores DSA glue state and embeds the Ocelot switch-library object.
- Exported prototypes are `felix_register_switch()`, `felix_port_to_netdev()`, and `felix_netdev_to_port()`.

## Control Flow
Chip-specific drivers construct a static `felix_info` and call `felix_register_switch()`. The shared library uses the function pointers and resource descriptions from `felix_info` during DSA setup and later DSA callbacks. Tag-protocol operations are selected internally in `felix.c`.

## State and Persistence Behavior
The header defines runtime state but does not persist it. `struct felix` is devm-allocated during probe and removed with the device. Its `tag_proto`, `tag_proto_ops`, and host flood masks are mutable runtime state. `switch_base` is used for hardcoded resource offsets, while `pcs` and `imdio` are optional runtime resources owned by chip-specific MDIO setup.

## Dependencies and Integration Points
The types reference DSA, Ocelot switch-library structures, phylink, PTP caps, VCAP props, Linux resources, device tree nodes, net devices, tc setup types, and chip-specific register maps. This header is included by `felix.c`, `felix_vsc9959.c`, `ocelot_ext.c`, and the Seville front end.

## Risks and Edge Cases
- `resource_names` must have `TARGET_MAX` elements because it is indexed directly by target enum.
- `port_modes` must cover all `num_ports`, or device-tree PHY validation can read invalid data.
- Optional callbacks must be null-checked by the shared library before use; new callbacks should follow that pattern.
- `quirk_no_xtr_irq` changes timestamp trap behavior and must only be set for hardware where the extraction interrupt is truly unavailable.
- The `struct felix` embedded `struct ocelot` means lifetime and pointer conversion assumptions are tightly coupled.

## Test Signals
Compile coverage should include all chip-specific users of `struct felix_info`. Runtime validation should confirm that each front end supplies complete resource names/maps, valid per-port modes, correct optional callbacks, and matching PTP/IRQ capabilities. Static analysis should flag unguarded optional callback dereferences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/felix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/felix_vsc9959.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/felix_vsc9959.c

## Purpose
This file is the PCI front end and hardware profile for the VSC9959/Felix switch embedded in the NXP LS1028A. It supplies register maps, resources, regfields, VCAP layouts, PTP capabilities, reset/watermark/MDIO callbacks, TSN scheduler offloads, PSFP stream filtering, cut-through forwarding policy, interrupt handling, and PCI probe/remove/shutdown glue to the shared Felix DSA library.

## Important APIs, Types, and Functions
- Static register maps (`vsc9959_ana_regmap`, `vsc9959_qs_regmap`, `vsc9959_vcap_regmap`, `vsc9959_qsys_regmap`, `vsc9959_rew_regmap`, `vsc9959_sys_regmap`, `vsc9959_ptp_regmap`, `vsc9959_gcb_regmap`, `vsc9959_dev_gmii_regmap`) map Ocelot targets to VSC9959 offsets.
- `vsc9959_resources` and `vsc9959_resource_names` describe PCI BAR-relative MMIO windows.
- `vsc9959_regfields` maps abstract Ocelot regfields to VSC9959 bit positions.
- `vsc9959_vcap_*` arrays and `vsc9959_vcap_props` define ES0, IS1, and IS2 key/action layouts.
- `vsc9959_ptp_caps` exposes Ocelot PTP clock operations.
- `vsc9959_reset()` performs GCB soft reset, SYS RAM initialization, and core enable polling.
- `vsc9959_wm_enc()`, `vsc9959_wm_dec()`, and `vsc9959_wm_stat()` implement hardware watermark conversion.
- `vsc9959_mdio_bus_alloc()` maps the internal MDIO controller, registers an ENETC-backed MDIO bus, and creates Lynx PCS instances for non-internal ports.
- TSN/TAS helpers include `vsc9959_tas_min_gate_lengths()`, `vsc9959_tas_guard_bands_update()`, `vsc9959_qos_port_tas_set()`, `vsc9959_tas_clock_adjust()`, `vsc9959_sched_speed_set()`, and `vsc9959_qos_port_cbs_set()`.
- PSFP types `struct felix_stream`, `struct felix_stream_filter`, and `struct felix_stream_gate` track stream identification, stream filters, gates, policers, and counters.
- PSFP operations are `vsc9959_psfp_filter_add()`, `vsc9959_psfp_filter_del()`, `vsc9959_psfp_stats_get()`, and initialization/list-management helpers.
- `vsc9959_cut_through_fwd()` computes safe cut-through egress TC masks based on forwarding-domain link speeds, oversize dropping, and MAC Merge preemptible TCs.
- `vsc9959_ops` and `felix_info_vsc9959` wire all hardware-specific behavior into the common Felix layer.
- `felix_pci_probe()`, `felix_pci_remove()`, and `felix_pci_shutdown()` implement PCI lifecycle for vendor/device ID Freescale `0xEEF0`.

## Control Flow
PCI probe enables the device, sets bus mastering, reads switch BAR 4 base, and calls `felix_register_switch()` with PTP and MAC Merge enabled, `OCELOT_NUM_TC` flooding PGIDs, initial `DSA_TAG_PROTO_OCELOT`, and `felix_info_vsc9959`. The shared Felix setup then consumes the resource maps and callbacks in this file.

Hardware reset first asserts the GCB soft reset bit and polls until it clears, initializes switch RAM through `SYS_RAM_INIT`, polls completion, then enables the switch core. MDIO allocation maps the internal MDIO resource from PCI BAR 0, allocates ENETC MDIO hardware, registers a Linux `mii_bus`, and creates Lynx PCS objects for configured external SerDes ports.

TAS setup validates command type, mqprio mapping, cycle time, cycle extension, and GCL length. For replace, it programs guard-band control, checks pending admin config errata, enables TAS, computes a base time in the future from PTP time, writes schedule parameters and GCL entries, commits config change with polling, stores a taprio reference, and recalculates guard bands. Destroy disables TAS, frees the taprio offload reference, resets queue mapping, and updates guard bands.

Guard-band calculation computes minimum continuous open windows per TC, frame transmission time at current speed, preemptible-fragment timing for MAC Merge, per-TC max SDU limits, and updates QMAXSDU plus port max SDU. Scheduler speed updates TAS speed encoding and recalculates guard bands under `fwd_domain_lock`.

PSFP add parses a flower rule that must match destination MAC and VLAN, then processes gate and police actions. It programs stream gates, policers, stream filter instances, source-port masks, and MAC table stream metadata under `psfp->lock`. Delete reverses SFI/SGI/policer state, updates stream table entries, and restores MAC stream metadata. Stats reads per-SFID counters under `stat_view_lock`, accumulates them into software counters, reports packets/drops, and clears the software snapshot.

Cut-through forwarding is recalculated under `fwd_domain_lock`. It enables cut-through only for up ports that are at the minimum speed in their forwarding domain and only for TCs without oversize dropping or preemption.

Remove unregisters DSA and disables the PCI device. Shutdown calls `dsa_switch_shutdown()` and clears driver data.

## State and Persistence Behavior
Most static arrays are immutable hardware description. Runtime state is held by the shared `struct ocelot`, `struct felix`, Lynx PCS objects, MDIO bus, taprio offload references in `ocelot_port->taprio`, MAC Merge state in `ocelot->mm`, and PSFP lists in `ocelot->psfp`. PSFP stream/filter/gate lists use refcounts to share hardware entries. Hardware table state is programmed into VSC9959 registers and is lost on reset; software reconstructs it from DSA/tc state only through normal setup/offload replay.

## Dependencies and Integration Points
The file integrates PCI, ENETC MDIO, Lynx PCS, Ocelot register/library APIs, PTP clock operations, DSA, phylink via the common layer, tc taprio/mqprio/CBS/flower gate/police actions, PSCHED timing, MAC Merge, devlink stats, and VCAP policers. It relies on shared Felix callbacks for DSA registration and netdev/port translation.

## Risks and Edge Cases
- Register maps and VCAP field offsets are hardware-contract data; a wrong offset corrupts unrelated switch state.
- TAS rejects cycles over one second and GCLs over 63 entries; users need clear extack/user feedback from upper layers.
- TAS admin config pending errata returns `-EBUSY`; repeated configuration attempts need to handle this.
- Guard-band logic must balance too-small windows, MTU changes, MAC Merge preemption, QMAXSDU side effects, and cut-through restrictions.
- `vsc9959_psfp_filter_del()` declares `static struct felix_stream_filter *sfi`, which is unusual for per-call temporary state and should be audited for concurrency/readability.
- PSFP stream identification only supports destination MAC plus VLAN, with optional PCP; unlearned MAC entries fail because stream metadata is attached through the MAC table.
- Shared SFI/SGI entries are refcounted; rollback paths must delete gates/policers exactly once.
- Internal MDIO PCS creation silently skips failed PCS creation for a port, which may leave a port without a PCS but not fail probe.
- Cut-through forwarding depends on current link speeds and forwarding-domain masks; stale speed or domain state could enable unsafe cut-through.

## Test Signals
Test signals include PCI probe/remove/shutdown, reset timeout handling, MMIO resource mapping, internal MDIO scan and PCS creation, all supported PHY modes, PTP clock registration and interrupt-driven TX timestamping, MAC Merge IRQ handling, taprio replace/destroy including base-time-in-past adjustment and pending-config `-EBUSY`, MTU-triggered guard-band recalculation, CBS/mqprio offloads, PSFP flower add/delete/stats for gate and police actions, rollback fault injection for PSFP partial failures, cut-through recalculation under link speed/bridge/LAG changes, and build coverage for all static register-map references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/felix_vsc9959.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/ocelot_ext.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/ocelot_ext.c -->
