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
