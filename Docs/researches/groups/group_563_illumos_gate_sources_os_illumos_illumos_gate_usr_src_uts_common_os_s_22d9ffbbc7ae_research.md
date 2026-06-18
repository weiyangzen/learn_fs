# Group Research: group_563_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_s_22d9ffbbc7ae

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. Both listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sunndi.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sunndi.c

## Purpose

`sunndi.c` implements core illumos NDI/DDI helper infrastructure around device-tree node management, devctl ioctl support, event delivery, device fault propagation, node metadata, and per-bus/private flavor storage. It is not filesystem-specific, but it is part of the OS substrate that storage and filesystem-adjacent drivers rely on for dynamic device configuration, hotplug, fault reporting, and bus event routing.

## Main Interfaces

Property helpers:
`ndi_prop_update_int`, `ndi_prop_update_int64`, `ndi_prop_create_boolean`, array/string/byte update variants, `ndi_prop_remove`, and `ndi_prop_remove_all` wrap `ddi_prop_update_common` and related DDI property removal functions with hardware-default property flags.

Event busop wrappers:
`ndi_post_event`, `ndi_busop_add_eventcall`, `ndi_busop_remove_eventcall`, and `ndi_busop_get_eventcookie` route event operations to responsible nexus busops, walking upward when an ancestor does not support the required event-cookie busop revision.

Devctl helpers:
`ndi_dc_allochdl` copies in native or 32-bit `devctl_iocdata`, copies optional child name/address strings, bounds-checks and unpacks user nvlist data, and returns a kernel-side handle. `ndi_dc_freehdl`, `ndi_dc_getname`, `ndi_dc_getaddr`, and `ndi_dc_get_ap_data` manage and access that handle.

Generic devctl operations:
`ndi_devctl_device_online`, `ndi_devctl_device_offline`, `ndi_devctl_device_remove`, `ndi_devctl_device_getstate`, `ndi_dc_return_dev_state`, `ndi_devctl_bus_getstate`, `ndi_dc_return_ap_state`, and `ndi_dc_return_bus_state` implement common bus/device ioctl behavior. `ndi_devctl_ioctl` dispatches supported commands and maps unsupported bus/AP/device reset and attachment-point controls to `ENOTSUP`.

Dynamic child creation:
`ndi_dc_devi_create` and static `i_dc_devi_create` create child `dev_info_t` nodes from nvlist-defined properties. Supported property nvpair types are `DATA_TYPE_INT32`, `DATA_TYPE_STRING`, `DATA_TYPE_BYTE_ARRAY`, `DATA_TYPE_INT32_ARRAY`, and `DATA_TYPE_STRING_ARRAY`. The public helper can return a constructed-but-not-online node, create an offline node, or bring it online and attach it.

Bus state:
`ndi_get_bus_state` reads soft bus state from `devi_lock`-protected flags and reports `BUS_QUIESCED`, `BUS_SHUTDOWN`, or `BUS_ACTIVE`. `ndi_set_bus_state` mutates the same state flags.

NDI event framework:
`ndi_event_alloc_hdl`, `ndi_event_free_hdl`, `ndi_event_bind_set`, `ndi_event_unbind_set`, `ndi_event_retrieve_cookie`, `ndi_event_add_callback`, `ndi_event_remove_callback`, `ndi_event_run_callbacks`, `ndi_event_do_callback`, and tag/name conversion helpers implement per-nexus event registration and callback dispatch. The framework enforces attach/detach-time event binding and prevents mixing high-level interrupt events with normal interrupt/kernel-context events in one handle.

Node and fault helpers:
The file exposes node classification and attribute helpers such as `ndi_dev_is_prom_node`, `ndi_dev_is_pseudo_node`, hidden/hotplug/persistent checks, setters/getters for node class/attributes/nodeid, and fault markers for access and DMA handles. The default fault handler/logger update device state on service loss/degradation/restoration and emit service-state messages.

Root nexus events:
`i_ddi_rootnex_init_events`, `i_ddi_rootnex_get_eventcookie`, `i_ddi_rootnex_add_eventcall`, `i_ddi_rootnex_remove_eventcall`, and `i_ddi_rootnex_post_event` provide the rootnex fault-event implementation using a static `rootnex_event_hdl`. Platform-overridable `plat_fault_handler` and `plat_fault_logger` default to local implementations.

Bus private/flavor storage:
`ndi_set_bus_private`, `ndi_get_bus_private`, `ndi_port_type`, `ndi_flavor_set`, `ndi_flavor_get`, `ndi_flavorv_alloc`, `ndi_flavorv_set`, and `ndi_flavorv_get` maintain per-port and per-child-flavor private data on devinfo nodes.

## Important Control Flow

Devctl input flow:
User ioctl data is copied into kernel memory, optional node name/address strings are copied with `MAXNAMELEN` bounds, packed nvlists are size-checked against `DEVCTL_MAX_NVL_USERSZ`, copied, and unpacked. All allocated pieces are released by `ndi_dc_freehdl`.

Device online/offline/remove flow:
The child name is built as `name@addr`, then online uses `ndi_devi_config_one` with `NDI_DEVI_ONLINE | NDI_CONFIG`, while offline/remove force devfs cache cleanup and call `ndi_devi_unconfig_one` with offline/remove flags. `NDI_BUSY` maps to `EBUSY`; `NDI_FAILURE` maps to `EIO`.

Child creation flow:
The nvlist must include `DC_DEVI_NODENAME`. The helper allocates a SID node, applies supported property types, then either returns it as constructed, marks it offline and initializes it, or brings it online with attach. Failures remove/free the partially created node.

Event lifecycle:
A handle owns a cookie list and two mutexes: one for event-handle metadata and one for callbacks. Bind adds non-duplicate cookies and updates high/other interrupt-level counts. Unbind first verifies that targeted events have no callbacks, then removes cookies. Callback execution holds only the callback mutex to avoid recursive use of the handle mutex by conversion routines.

## Locking and Resource Notes

Device state and bus state are protected by `DEVI(dip)->devi_lock`. Device-tree child lookup uses `ndi_devi_enter`/`ndi_devi_exit` around parent traversal. Event operations use `ndi_evthdl_mutex` plus `ndi_evthdl_cb_mutex`; callback execution deliberately avoids holding `ndi_evthdl_mutex`.

Memory ownership is explicit: copied devctl strings, unpacked nvlists, event cookies, callback records, and flavor vectors are allocated with `kmem_*` and released on normal and most error paths. Devctl ioctl handling always frees the copied handle after dispatch.

## Research Notes

This file is a central illumos device-framework utility layer. For storage/filesystem research, the most relevant surfaces are dynamic device creation/removal, devfs cache invalidation on device state changes, event delivery to nexus drivers, fault-state propagation, and the rootnex fault event path used by lower-level bus/storage drivers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sunndi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sunpci.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sunpci.c

## Purpose

`sunpci.c` implements common PCI configuration-space helpers and suspend/resume preservation logic. It saves and restores PCI/PCIe config registers, selected capability registers, and PCI power-management context, including PME wake behavior. This matters to storage and filesystem-adjacent drivers because block devices often sit behind PCI/PCIe controllers whose configuration must survive suspend, resume, detach, and reattach cycles.

## Main Interfaces

Config access:
`pci_config_setup` maps PCI config space register set 0 with little-endian strict-order access and enables fault-managed access when the device supports it. `pci_config_teardown` unmaps it. `pci_config_get8/16/32/64` and `pci_config_put8/16/32/64` derive the mapped address from the access handle and perform typed DDI reads/writes.

Config save/restore:
`pci_save_config_regs` snapshots config registers into devinfo properties. `pci_restore_config_regs` restores those properties and removes them afterward.

Capability save/restore:
`pci_save_caps`, `cap_walk_and_save`, `pci_fill_buf`, `pci_generic_save`, `pci_msi_save`, `pci_pcix_save`, `pci_pcie_save`, `pci_ht_addrmap_save`, `pci_ht_funcext_save`, `pci_pmcap_check`, and `pci_restore_caps` implement capability walking and replay. `pci_cap_table` describes supported capability IDs and capability-specific sizing functions.

Power management:
`pci_lookup_pmcap` finds the PCI PM capability for ordinary header-zero devices. `pci_post_suspend` saves config state, computes an appropriate low-power suspend level with PME enable when possible, disables I/O/memory/bus mastering, optionally enables ACPI wake on x86, and writes PMCSR last. `pci_pre_resume` disables wake, restores PMCSR/D0 timing, and restores saved config space.

## Important Control Flow

PCIe save path:
If capability walking detects `PCI_CAP_ID_PCI_E`, the code allocates a 4 KiB PCIe config buffer plus a readable-word mask. On SPARC it uses `ddi_peek32`; on x86 it uses cautious config access and treats `0xffffffff` as unreadable. It stores `SAVED_CONFIG_REGS_MASK` and `SAVED_CONFIG_REGS` properties.

Conventional PCI save path:
For non-PCIe devices, it saves selected header fields into `pci_config_header_state_t`: command, header type, bridge control for type-one headers, cache line size, latency timers, and BAR0-BAR5. It then saves supported PCI capabilities into a trailing register buffer and stores descriptors in `SAVED_CONFIG_REGS_CAPINFO`.

Capability sizing:
MSI save length depends on 64-bit-address and per-vector-mask support. PCI-X save length depends on version. HyperTransport address-map and function-extension capabilities compute variable lengths from capability registers. PCIe capability save returns zero because PCIe devices are handled by the 4 KiB full-config save path.

Restore path:
PCIe restore replays only masked readable 32-bit words. Conventional restore writes saved command/header-related values, BARs, and saved capability registers. PM capability restore preserves current power-state bits through `pci_pmcap_check` so restoring config space does not accidentally force an unwanted D-state. A final read flushes writes before saved properties are removed.

Suspend path:
`pci_post_suspend` first saves config regs, then caches PM context in `SAVED_PM_CONTEXT`. If no PM capability exists, it records `PPCF_NOPMCAP`. Otherwise it chooses the lowest PME-capable state, preferring D3 hot/cold, then D2, D1, D0, falling back to D3 hot. It clears command-register I/O, memory, and bus master enables before writing PMCSR last.

Resume path:
`pci_pre_resume` reads saved PM context, disables platform wake on x86 if it was enabled, restores PMCSR, delays 10 ms for D3-to-D0 timing, and calls `pci_restore_config_regs`.

## Data and Properties

Persisted device properties:
`SAVED_CONFIG_REGS`, `SAVED_CONFIG_REGS_MASK`, `SAVED_CONFIG_REGS_CAPINFO`, and local `SAVED_PM_CONTEXT` hold suspend/detach context across the relevant framework transitions.

Global control:
`pci_enable_wakeup` gates PME/platform wake handling.

## Research Notes

This file is the common PCI state-preservation layer for illumos. The key storage-relevant behavior is that PCIe devices get full 4 KiB cautious snapshots, while conventional PCI devices get header plus selected capability replay. Power-management code carefully writes PMCSR last on suspend and restores PMCSR before config registers on resume, which is important for devices that stop responding correctly after entering D3.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sunpci.c -->