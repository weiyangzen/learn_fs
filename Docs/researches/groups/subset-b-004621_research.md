<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef10.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef10.c

## Purpose
Implements the Solarflare/Xilinx SFC EF10 hardware backend, including Huntington, Medford, Medford2, and X4 style NIC types. It supplies the `struct efx_nic_type` operation tables used by the common SFC driver for PF and VF probe, reset, interrupt/event processing, DMA queue setup, filtering, statistics, VLAN handling, UDP tunnel offload, PTP, NVRAM/MTD, SR-IOV/vswitch hooks, and MAC address management.

## Important APIs, Types, And Functions
- `struct efx_ef10_vlan` tracks VLAN IDs mirrored into the MCDI filter table under `nic_data->vlan_lock`.
- Probe/remove and resource functions: `efx_ef10_probe()`, `efx_ef10_probe_pf()`, `efx_ef10_probe_vf()`, `efx_ef10_remove()`, `efx_ef10_dimension_resources()`, `efx_ef10_init_nic()`, `efx_ef10_fini_nic()`.
- MCDI and reset functions: `efx_ef10_mcdi_request()`, `efx_ef10_mcdi_poll_response()`, `efx_ef10_mcdi_poll_reboot()`, `efx_ef10_mcdi_reboot_detected()`, `efx_ef10_reset()`, `efx_ef10_table_reset_mc_allocations()`.
- Datapath functions: `efx_ef10_tx_probe()`, `efx_ef10_tx_init()`, `efx_ef10_tx_write()`, `efx_ef10_rx_write()`, `efx_ef10_ev_process()`, `efx_ef10_handle_rx_event()`, and TX timestamp handling in `efx_ef10_handle_tx_event()`.
- Exported NIC type tables: `efx_hunt_a0_vf_nic_type`, `efx_hunt_a0_nic_type`, and `efx_x4_nic_type`.

## Control Flow
Probe allocates `efx_ef10_nic_data`, an MCDI DMA buffer, learns the warm-boot count, cancels stale kexec-era MCDI requests, initializes MCDI, resets the function, enables event logging, exposes sysfs flags, reads PF/capability information, sizes VIs and channels, obtains MAC/port/timer/monitor data, initializes PTP, and seeds default VLAN filter state. Resource dimensioning allocates VIs, optionally allocates PIO buffers, remaps the BAR into UC and optional WC regions, and links PIO buffers to VIs and TX queues. Runtime traffic flows through the common netdev into EF10 TX descriptor construction and event queue completion handlers; RX events decode scatter/merge state, checksum/classification bits, and queue labels before delivering packets to the common RX path. Removal reverses VLANs, PTP, monitor, RSS, PIO/VI, sysfs, tunnel, MCDI, and buffer allocations.

## State And Persistence
Persistent driver state is in `efx_ef10_nic_data`: MCDI buffer, warm boot counter, capability bitmasks, firmware IDs, PIO handles/mappings, allocated VI base/count, VLAN list, UDP tunnel table and dirty flag, stats buffers/counters, licensed features, port ID, PF/VF metadata, and reset recovery flags. Firmware resources are not durable across MC reset, FLR, or port reset; the file explicitly marks VIs, filters, RSS contexts, PIO buffers, and vswitch/vport IDs for reallocation. NVRAM partition exposure is persistent hardware storage but is accessed via MCDI/MTD helpers rather than cached in this file.

## Dependencies And Integration Points
Depends on `net_driver.h`, common RX/TX paths, EF10 register definitions, MCDI protocol/functions, MCDI filters/ports, workarounds, selftests, SR-IOV helpers, Linux UDP tunnel offload APIs, PTP, MTD, and ethtool-facing common callbacks. It integrates with the broader SFC lifecycle through the `efx_nic_type` vtable and with firmware through many `MC_CMD_*` RPCs.

## Risks And Edge Cases
High-risk areas are reset recovery and failure unwind: MC reboot invalidates allocations; PIO and VI counts can be partial; BAR remaps must leave coherent UC/WC state; UDP tunnel table changes can trigger MC reset; VF/PF cross-links can be stale after PF unload; stat generation reads can race firmware DMA; timestamp queues require licensed features; and RX event pointer/classification inconsistencies schedule resets. VLAN VID 0 is intentionally retained for untagged traffic, so cleanup must not treat normal 8021q removal as final state.

## Test Signals
Useful signals include successful PF/VF probe and remove, interface up/down, VI allocation fallback, traffic with scatter/merge RX, TSO v1/v2, encapsulated offloads, VLAN filtering, UDP tunnel add/remove, PTP timestamp configuration, SR-IOV VF lifecycle, ethtool stats/FEC, MTD partition discovery, selftest BIST, interrupt tests, and reset paths for MC reboot, FLR, TX watchdog, and MCDI timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100.c

## Purpose
Provides the PCI driver and early PCI capability discovery for EF100/Riverhead devices. It finds the EF100 function-control window, maps the correct BAR, binds PCI device IDs to PF/VF NIC type tables, calls the EF100 NIC and netdev probes, handles PCI remove, and forwards SR-IOV configuration requests.

## Important APIs, Types, And Functions
- `struct ef100_func_ctl_window` records whether a discovered function-control window is valid, which BAR contains it, and its offset.
- `ef100_pci_find_func_ctrl_window()`, `ef100_pci_parse_xilinx_cap()`, `ef100_pci_walk_xilinx_table()`, `ef100_pci_parse_ef100_entry()`, and `ef100_pci_parse_continue_entry()` parse Xilinx vendor-specific PCI extended capabilities and chained BAR tables.
- `ef100_pci_probe()` allocates `efx_probe_data`, initializes common `efx_nic` state, maps I/O, calls `efx->type->probe()`, and creates the netdev.
- `ef100_pci_remove()` tears down netdev/devlink/SR-IOV related state, NIC state, I/O mappings, and allocated probe data.
- `ef100_pci_driver` exports the Linux `struct pci_driver`; `ef100_pci_table` maps Xilinx device IDs `0x0100` and `0x1100` to PF/VF EF100 NIC types.

## Control Flow
Probe initializes the common NIC structure with a default VI stride, searches all PCI vendor extended capabilities for a Xilinx config BAR table, temporarily maps continuation BARs while walking chained tables, validates entry lengths/revisions/BAR values, and falls back to BAR 2 offset 0 when no Xilinx capability is found. After validating the window bounds against BAR length, it maps the selected BAR, sets `efx->reg_base`, runs the NIC-type probe from `ef100_nic.c`, marks the device probed, and calls `ef100_probe_netdev()`. Any probe failure funnels into `ef100_pci_remove()` for symmetric cleanup.

## State And Persistence
State created here is PCI driver data, `struct efx_probe_data`, the common `efx_nic`, BAR mapping metadata, and `efx->reg_base`. It does not persist hardware configuration itself; it discovers and maps the register aperture needed by later MCDI/NIC code. The capability walk temporarily mutates BAR mappings and must restore previous mappings after continuation-table parsing.

## Dependencies And Integration Points
Depends on Linux PCI APIs, SFC common structure setup/teardown, I/O mapping helpers, EF100 register bit definitions, EF100 NIC type tables from `ef100_nic.c`, netdev lifecycle in `ef100_netdev.c`, and SR-IOV support from `ef100_sriov.h`. It is the module-facing PCI integration point for EF100 hardware.

## Risks And Edge Cases
Capability parsing has several hardware-facing risks: duplicate EF100 entries, invalid expansion-ROM/invalid BAR IDs, too-short table entries, table offsets that overrun BAR resources, failed temporary BAR remaps, and failure to restore the original BAR after walking continuation tables. The fallback default BAR path is necessary for devices without the extension but can mask platform assumptions. Remove must tolerate partially probed devices and `NULL` driver data.

## Test Signals
Test by probing PF and VF IDs, booting devices with and without Xilinx extended capability tables, exercising continuation-table entries in alternate BARs, forcing invalid table metadata, loading/unloading the module, hot-removing the PCI function, and invoking SR-IOV VF count changes. Kernel logs around function-control window discovery and "initialisation successful" are direct probe signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100.h

## Purpose
Declares the EF100 PCI driver object so other SFC module code can register or reference the EF100 PCI bus binding.

## Important APIs, Types, And Functions
- `extern struct pci_driver ef100_pci_driver;` is the only public symbol in this header.

## Control Flow
No runtime control flow is implemented. Including this header gives module initialization code access to the PCI driver defined in `ef100.c`.

## State And Persistence
No state is owned here. The referenced `pci_driver` persists as a static driver descriptor in the module binary and is registered with Linux PCI core elsewhere.

## Dependencies And Integration Points
Integrates `ef100.c` with module registration code. Consumers must already be in a context where Linux PCI declarations are visible or available through included kernel headers.

## Risks And Edge Cases
The header intentionally has no include guard and no include list in this snapshot, which is acceptable for a single extern declaration but fragile if expanded. Adding definitions here should introduce a normal guard and required type includes.

## Test Signals
Build coverage is the main signal: EF100 module compilation and successful PCI driver registration prove the declaration matches the definition in `ef100.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_ethtool.c

## Purpose
Defines EF100-specific ethtool operations, mostly by wiring common SFC ethtool helpers to an EF100 netdevice and adding EF100 descriptor-ring size reporting.

## Important APIs, Types, And Functions
- `EFX_EF100_MAX_DMAQ_SIZE` sets the advertised maximum RX/TX ring size to 16384 descriptors.
- `ef100_ethtool_get_ringparam()` reports current `efx->rxq_entries` and `efx->txq_entries` plus EF100 max queue sizes.
- `const struct ethtool_ops ef100_ethtool_ops` publishes driver info, message level, pause, link settings, selftest, string/stat, RX NFC, reset, RSS context, module EEPROM, FEC, and ring parameter handlers.

## Control Flow
The netdev registration code assigns `net_dev->ethtool_ops = &ef100_ethtool_ops`. User ethtool requests then enter either the small EF100 ringparam helper or common SFC helpers. This file does not implement setters for ring size; it only exposes current and maximum values.

## State And Persistence
No private state is allocated. Reported state comes from the live `efx_nic` embedded behind the netdevice. Changes made by common ethtool operations, such as pause, FEC, RSS context, reset, or link settings, are handled by shared SFC code and/or firmware, not cached here.

## Dependencies And Integration Points
Depends on Linux ethtool/netdevice APIs, `efx_netdev_priv()`, common ethtool helpers in `ethtool_common.h`, MCDI port helpers, RSS context private sizing, and EF100 netdev registration. It is the user-space observability/control surface for EF100 netdevices.

## Risks And Edge Cases
The max ring size is a static QDMA hardware limit; actual allocation may be lower due to VI/channel constraints elsewhere. Because ringparam has no EF100 setter here, user expectations for resizing depend on common behavior and may differ from reported maxima. RSS context operations rely on shared code correctly interpreting EF100 capabilities.

## Test Signals
Run `ethtool -i`, `ethtool -g`, `ethtool -S`, `ethtool -k`, RSS indirection/key commands, FEC get/set, module EEPROM reads, selftests, and reset commands on an EF100 netdevice. Correct ringparam output should show max 16384 and current queue sizes from the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_ethtool.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_ethtool.h

## Purpose
Publishes the EF100 ethtool operation table for netdevice registration.

## Important APIs, Types, And Functions
- `extern const struct ethtool_ops ef100_ethtool_ops;` is consumed by `ef100_netdev.c`.

## Control Flow
No executable control flow exists. The declaration lets `ef100_register_netdev()` attach the operations table defined in `ef100_ethtool.c`.

## State And Persistence
No runtime state is owned here. The declared object is immutable operation-table metadata.

## Dependencies And Integration Points
Integrates EF100 netdev setup with ethtool handling. Consumers need Linux `struct ethtool_ops` visibility via existing kernel includes.

## Risks And Edge Cases
Like `ef100.h`, this is a minimal declaration-only header without an include guard. It is safe as written, but future expansion should add a guard and explicit ethtool type includes.

## Test Signals
Compile-time linkage and successful `net_dev->ethtool_ops` assignment validate this header. Runtime ethtool command success validates the linked table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_ethtool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_netdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_netdev.c

## Purpose
Owns EF100 netdevice creation, registration, open/stop, transmit entry, notifier integration, and netdevice teardown. It bridges PCI/NIC probe state from `ef100.c` and `ef100_nic.c` into the Linux networking stack.

## Important APIs, Types, And Functions
- `ef100_probe_netdev()` allocates `alloc_etherdev_mq()`, configures features, probes datapath caps/PHY/channels/filter table, gets MAC address, registers devlink/netdev/notifiers, and performs PF-only MAE/SR-IOV setup.
- `ef100_remove_netdev()` closes and unregisters the netdevice, disables SR-IOV, tears down devlink/TC/filter/channel/PHY state, and frees `net_device`.
- `ef100_net_open()` and `ef100_net_stop()` implement interface up/down.
- `__ef100_hard_start_xmit()` is shared by the PF netdevice and representor TX path.
- `ef100_netdev_ops`, `ef100_netdev_event()`, and `ef100_netevent_event()` integrate Linux netdev and netevent callbacks.

## Control Flow
Probe exits early when firmware reports no active network port. Otherwise it allocates a netdev with private storage pointing back to `efx_probe_data`, enables supported offloads except RX-FCS/RX-all by default, applies TSO limits from EF100 design parameters, initializes caps/PHY/channels/filtering/RSS/MAC/devlink, registers the netdev, runs PF-only representor/TC/devlink-port setup, then registers netdevice and netevent notifiers. Open probes interrupts, sizes channels, frees/reallocates VIs, retries with fewer channels when VI allocation is short, probes channels, remaps the BAR to allocated VI count, initializes NAPI/filters/interrupts/stats, starts queues, polls PHY, and attaches representors. Stop detaches representors, stops queues, shuts down datapath/statistics/interrupts/filters/NAPI/channels/VIs in reverse order.

## State And Persistence
State includes the allocated `net_device`, `efx->name`, feature flags, queue limits, registered notifier blocks, devlink lock/registration state, filter table, channels, PHY data, interrupt resources, and `efx->state` transitions among probed, net down, and net up. No disk persistence exists; state is kernel runtime plus firmware allocations.

## Dependencies And Integration Points
Depends on common SFC netdev helpers, MCDI port/filter functions, EF100 NIC functions, EF100 TX implementation, EF100 ethtool ops, SR-IOV, TC/MAE, encap actions, RX common code, Linux notifier APIs, rtnl locking, and devlink helpers. Representor TX calls `__ef100_hard_start_xmit()` from `ef100_rep.c`.

## Risks And Edge Cases
Probe failure after partial devlink registration or notifier setup requires careful cleanup; this file mostly jumps to `fail` and relies on remove-style cleanup. VI allocation retry changes `efx->max_channels`, so channel/interrupt assumptions must be recalculated. `ef100_net_open()` returns directly on `efx_probe_channels()` failure rather than going through `fail`, which is notable for cleanup review. TX drops always return `NETDEV_TX_OK` after freeing the skb and incrementing stats. Notifier forwarding is conditional on MAE privilege.

## Test Signals
Signals include netdevice registration/unregistration, `ip link set up/down`, interrupt allocation, NAPI creation, VI shortage retry behavior, TX under normal and no-channel conditions, RSS default table programming, MAC address provisioning for PF/VF, devlink registration, SR-IOV disable on removal, and TC/netevent callbacks when `grp_mae` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_netdev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_netdev.h

## Purpose
Declares EF100 netdevice lifecycle and transmit entry points shared between the PF/VF netdevice implementation and representor code.

## Important APIs, Types, And Functions
- `__ef100_hard_start_xmit()` is the common transmit helper accepting an optional `struct efx_rep *` to tag representor-originated traffic.
- `ef100_netdev_event()` is the netdevice notifier callback declaration.
- `ef100_probe_netdev()` and `ef100_remove_netdev()` expose netdevice setup/teardown to the PCI driver.

## Control Flow
No logic is implemented here. `ef100.c` calls probe/remove declarations during PCI lifecycle, and `ef100_rep.c` calls the shared TX helper when a representor transmits.

## State And Persistence
No state is owned. The prototypes operate on `struct efx_probe_data`, `struct efx_nic`, `struct net_device`, `struct sk_buff`, and optional representor state managed in implementation files.

## Dependencies And Integration Points
Includes Linux netdevice declarations and `ef100_rep.h` for the representor pointer type. It is a dependency bridge between `ef100_netdev.c`, `ef100.c`, and `ef100_rep.c`.

## Risks And Edge Cases
The header includes `ef100_rep.h`, while `ef100_rep.h` includes common driver types; care is needed to avoid future circular include growth. The shared TX helper must preserve semantics for both physical netdev and representor callers.

## Test Signals
Build coverage validates prototypes. Runtime validation comes from both normal PF/VF TX and representor TX paths reaching `__ef100_hard_start_xmit()` successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_netdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_nic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_nic.c

## Purpose
Implements the EF100 NIC-type backend below the Linux netdevice layer: MCDI transport, firmware capability and design-parameter discovery, event queue processing, interrupts, PHY/filter/MAC/reset handling, statistics, MAE/representor initialization, client ID lookup, and PF/VF `struct efx_nic_type` operation tables.

## Important APIs, Types, And Functions
- MCDI transport: `ef100_mcdi_request()`, `ef100_mcdi_poll_response()`, `ef100_mcdi_read_response()`, `ef100_mcdi_poll_reboot()`.
- Capability and design parsing: `efx_ef100_init_datapath_caps()`, `ef100_check_design_params()`, `ef100_tlv_feed()`, `ef100_process_design_param()`, `ef100_check_caps()`.
- Runtime datapath hooks: `ef100_ev_probe()`, `ef100_ev_init()`, `ef100_ev_process()`, `ef100_ev_read_ack()`, `ef100_msi_interrupt()`, `ef100_filter_table_up()`, `ef100_filter_table_down()`, `ef100_reconfigure_mac()`, `ef100_reset()`.
- Probe/remove: `ef100_probe_main()`, `ef100_probe_netdev_pf()`, `ef100_probe_vf()`, `ef100_remove()`.
- Exported NIC types: `ef100_pf_nic_type` and `ef100_vf_nic_type`.

## Control Flow
`ef100_probe_main()` allocates `ef100_nic_data`, initializes default TSO design limits, reads TLV design parameters from MMIO, allocates an aligned MCDI DMA buffer, samples warm-boot count with retry, cancels stale requests, initializes MCDI, resets the function, enables logging, reads PF index/port/firmware version/privilege mask, rejects old firmware and unsolicited-event-credit firmware, then returns to the PCI/netdev layers. Event processing uses a per-channel phase bit, reads qwords until phase mismatch or quota, dispatches RX events to EF100 RX code, MCDI events to common MCDI, TX completions to EF100 TX code, and driver events to logging. PF netdev probe conditionally initializes TC, base/own mports, MAE, representor enumeration, and hardware TC feature flags.

## State And Persistence
`struct ef100_nic_data` stores MCDI buffer, datapath capability masks, PF index, warm boot count, port ID, event queue phase bitmap, statistics cache, base/own mports, local MAE interface, MAE privilege flag, and TSO limits derived from hardware design parameters. Statistics are cached in memory and refreshed from firmware DMA stats. Firmware allocations and MCDI state are runtime-only and cleaned by `ef100_remove()`.

## Dependencies And Integration Points
Depends on EF100 registers, common SFC lifecycle/channel helpers, MCDI protocol/functions/filters/port code, EF100 RX/TX files, SR-IOV, netdev bridge, TC/MAE, selftest, and RX common code. Its `efx_nic_type` tables are consumed by the PCI driver and common SFC core.

## Risks And Edge Cases
Design-parameter parsing rejects unsupported queue granularity, oversized TLVs, unknown compatibility bits, and truncated TLV streams. Firmware version `< 1.1.0.1000` and unsolicited-event credits are explicitly rejected. MCDI doorbell word order is unusual. `ef100_mcdi_reboot_detected()` is empty, so reboot recovery differs from EF10 and relies on higher-level reset behavior. Stats allocation is `GFP_ATOMIC`; failure yields no update. PF representor/MAE failures are mostly nonfatal but can leave traffic features unavailable.

## Test Signals
Test probe with valid/invalid design TLVs, warm-boot retry, MCDI RPCs, firmware version gating, interface up/down, RX/TX/MCDI/driver events, interrupt test generation, reset types, PHY configuration, filter table add/remove, ethtool stats, MAE privilege and representor creation, PF and VF probe/remove, and client handle lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_nic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_nic.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_nic.h

## Purpose
Defines EF100 NIC-level public contracts: PF/VF NIC type exports, probe/remove helpers, statistics indices, private NIC data layout, capability-testing macro, and MCDI-facing helper prototypes.

## Important APIs, Types, And Functions
- `extern const struct efx_nic_type ef100_pf_nic_type` and `ef100_vf_nic_type`.
- `enum { EF100_STAT_* }` extends generic stats with EF100 MAC counters.
- `struct ef100_nic_data` is the central EF100 private state object.
- `efx_ef100_has_cap(caps, flag)` maps MCDI capability names to bit tests.
- Prototypes include `efx_ef100_init_datapath_caps()`, `ef100_phy_probe()`, `ef100_filter_table_probe()`, `ef100_get_mac_address()`, and `efx_ef100_lookup_client_id()`.

## Control Flow
No executable control flow exists. The header shapes how `ef100_nic.c`, `ef100_netdev.c`, SR-IOV, TC/MAE, and representor files share EF100 runtime state and invoke NIC-level services.

## State And Persistence
`struct ef100_nic_data` persists for the lifetime of a probed EF100 NIC. It stores firmware capability masks, the MCDI buffer, warm boot count, PF index, event queue phases, stats, port and mport identities, MAE privilege/local interface discovery flags, and hardware TSO limits.

## Dependencies And Integration Points
Includes common SFC `net_driver.h` and `nic_common.h`. It is the integration contract for EF100 PCI, netdev, SR-IOV, MAE/TC, representor, RX/TX, and ethtool code that need NIC type tables or private EF100 state.

## Risks And Edge Cases
Fields in `ef100_nic_data` are consumed across multiple files; initialization order matters. For example TSO limits must be populated before netdev TSO max setters, and MAE flags must be valid before notifier/representor code acts on them. Capability macro correctness depends on MCDI field naming staying aligned with `mcdi_pcol.h`.

## Test Signals
Compile-time checks catch enum/prototype mismatch. Runtime signals include valid stats names/counts, correct TSO limits on netdev, mport/MAE feature behavior, PF/VF type dispatch, and successful MCDI capability/mac/client helper calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_nic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_regs.h

## Purpose
Provides EF100/Riverhead hardware architecture constants: MMIO register offsets, register strides/rows, bitfield positions and widths, host-memory descriptor layouts, event encodings, PCI vendor capability table fields, RX prefix fields, TX descriptor formats, design-parameter IDs/defaults, and protocol enumerations.

## Important APIs, Types, And Functions
- Register offsets include `ER_GZ_MC_SFT_STATUS`, MCDI doorbells, event queue prime/timer/credit registers, RX/TX ring doorbells, hardware time, and design-parameter TLV registers.
- Descriptor/event field macros define RX descriptors/prefixes, TX send/segment/TSO/override/mem2mem formats, RX packet events, TX completions, driver events, timestamp events, and EF100 event type enumerators.
- PCI capability macros define Xilinx config BAR VSEC and table entries used by `ef100.c`.
- Design parameter enums/defaults define TLV types consumed by `ef100_nic.c`.

## Control Flow
No code executes here. The macros are consumed by I/O helpers and `EFX_*FIELD*` packing/unpacking macros in EF100 PCI, NIC, RX, and TX code. Control flow in those files depends on these constants matching hardware layout exactly.

## State And Persistence
No software state is stored. The header describes hardware state exposed through MMIO registers and DMA descriptor/event memory. Constants such as `ESE_GZ_FCW_LEN`, `ESE_GZ_RX_PKT_PREFIX_LEN`, and TSO defaults directly influence runtime allocation and parsing decisions.

## Dependencies And Integration Points
Included by EF100 PCI/NIC/netdev/RX/TX files and indirectly by common register access macros. It integrates the driver with EF100 firmware/hardware ABI and MCDI-adjacent layout expectations.

## Risks And Edge Cases
Incorrect bit offsets or widths can corrupt DMA descriptors, misread events, map the wrong BAR window, mishandle RX checksum/classification, or reject valid hardware design parameters. Event phase fields must align between RX and TX completions. PCI table constants must match firmware/FPGA capability structures or probe can fail. There is no runtime validation for most definitions beyond hardware behavior.

## Test Signals
Signals are integration-level: successful PCI capability discovery, MCDI doorbells, EVQ priming, RX/TX doorbells, packet RX prefix parsing, TX offloads including TSO/checksum/VLAN, event dispatch, design-parameter parsing, and absence of hardware warnings/resets during traffic. Build failures also reveal renamed or missing field macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_rep.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_rep.c

## Purpose
Implements EF100 VF representor netdevices for MAE/TC switching. Representors expose per-VF Linux netdevices, support TC flower/block offload binding, transmit through the parent EF100 TX path with representor context, receive packets queued from the parent RX path, and maintain software stats/devlink-port integration.

## Important APIs, Types, And Functions
- Netdev ops: `efx_ef100_rep_open()`, `efx_ef100_rep_close()`, `efx_ef100_rep_xmit()`, `efx_ef100_rep_get_port_parent_id()`, `efx_ef100_rep_get_phys_port_name()`, `efx_ef100_rep_setup_tc()`, `efx_ef100_rep_get_stats64()`.
- Lifecycle: `efx_ef100_vfrep_create()`, `efx_ef100_vfrep_destroy()`, `efx_ef100_fini_vfreps()`, `efx_ef100_init_reps()`, `efx_ef100_fini_reps()`.
- RX queueing: `efx_ef100_rep_rx_packet()` and NAPI poll `efx_ef100_rep_poll()`.
- Lookup/helpers: `efx_ef100_find_rep_by_mport()`, `ef100_mport_on_local_intf()`, `ef100_mport_is_vf()`.

## Control Flow
Creation allocates an etherdev with `struct efx_rep` private state, initializes lists/locks/default rule fields, adds it to `efx->vf_reps`, sets carrier/queue state based on the parent netdevice, configures netdev/ethtool ops, looks up the VF mport, configures a default TC rule, binds a devlink port, and registers the netdev. TX increments attempted TX stats and calls `__ef100_hard_start_xmit()` under the parent TX lock. RX copies a parent RX buffer into a new skb, queues it on `efv->rx_list`, and schedules NAPI; poll drains up to weight and reschedules if producer state advanced during delivery. Destruction unregisters the netdev, removes devlink/default rule/list membership, synchronizes RCU, and frees the netdev.

## State And Persistence
Representor state lives in `struct efx_rep`: parent pointer, netdev, message mask, mport, VF index, pseudo-ring write/read counters and size, default TC rule, list node, skb queue, spinlock, NAPI, atomic software stats, and devlink port pointer. This is runtime-only and tied to the parent PF/MAE lifetime.

## Dependencies And Integration Points
Depends on rhashtable for MAE mport cleanup, EF100 netdev shared TX, EF100 NIC private data, MAE enumeration/lookup, RX common buffers, TC bindings, and devlink helpers. It integrates with Linux representor semantics through port parent ID/name, TC setup, ethtool stats/ringparam, NAPI, and netdev registration.

## Risks And Edge Cases
The pseudo RX ring uses unsigned write/read arithmetic and drops when backlog exceeds `rx_pring_size`; very large user-set ring sizes can change memory pressure. RX copies with `GFP_ATOMIC`-style netdev allocation and drops on allocation failure. Lookup requires caller RCU protection plus internal list spinlock. TX stats count attempts, not success. Creation failure paths must undo devlink/default rules/list membership in the right order.

## Test Signals
Create/destroy VFs with MAE privilege, verify representor netdevices and devlink ports, check phys port names like `p%upf%uvf%u`, run traffic through VF representors, inspect software stats, exercise TC flower/block offloads, adjust representor RX ringparam, force RX backlog drops, and remove the parent PF while representors exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_rep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_rep.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_rep.h

## Purpose
Defines the EF100 representor data model and public representor lifecycle/RX/lookup helpers used by EF100 MAE, TC, netdev, and RX code.

## Important APIs, Types, And Functions
- `struct efx_rep_sw_stats` contains atomic RX/TX packet, byte, drop, and error counters.
- `struct efx_rep` stores parent PF, representor netdev, mport/VF identity, pseudo-ring counters and size, default TC rule, list node, RX list/lock, NAPI object, stats, and devlink port.
- Public functions include `efx_ef100_vfrep_create()`, `efx_ef100_vfrep_destroy()`, `efx_ef100_fini_vfreps()`, `efx_ef100_rep_rx_packet()`, `efx_ef100_find_rep_by_mport()`, `efx_ef100_init_reps()`, `efx_ef100_fini_reps()`, `ef100_mport_on_local_intf()`, and `ef100_mport_is_vf()`.
- Exports `efx_ef100_rep_netdev_ops`.

## Control Flow
No implementation exists here. The declarations support representor creation/destruction from SR-IOV/MAE control paths, RX dispatch from EF100 receive processing, mport-to-representor lookup under RCU, and TC/default-rule lifecycle in `ef100_rep.c`.

## State And Persistence
The primary state contract is `struct efx_rep`, whose lifetime is bound to a representor netdevice and parent PF. Software counters are atomic because updates can occur from TX/RX paths. The RX list and pseudo-ring counters persist queued packets until NAPI drains them.

## Dependencies And Integration Points
Includes common SFC driver types and TC rule definitions. Forward-declares `struct devlink_port` and `struct mae_mport_desc` to connect representors with devlink and MAE without exposing their full definitions here.

## Risks And Edge Cases
Cross-file users must respect locking documented in comments: mport lookup callers must hold `rcu_read_lock()`. RX queue fields require `rx_lock` protection. Default-rule state is embedded, so lifecycle code must initialize and deconfigure it exactly once. Adding fields used in fast paths may require cacheline/locking review.

## Test Signals
Build coverage validates users of the declarations. Runtime signals include correct representor allocation, TC rule binding, RX delivery via `efx_ef100_rep_rx_packet()`, safe RCU lookup by mport, accurate atomic stats, and clean teardown with no list or NAPI use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_rep.h -->
