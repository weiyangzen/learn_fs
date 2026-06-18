# sources/distributed-fs/ceph-client/drivers/rapidio/rio.c

## Purpose
Implements RapidIO core services: global device/net/mport registries, resource allocation for mailboxes and doorbells, port-write handling, memory window mapping, extended-feature discovery, route-table operations, optional DMA wrappers, scan registration, mport scanning, and mport lifecycle.

## Important APIs, types, and functions
Global state includes `rio_devices`, `rio_nets`, `rio_mports`, `rio_scans`, `rio_global_list_lock`, `rio_mport_list_lock`, and `rio_mmap_lock`. Public APIs include `rio_alloc_net/add_net/free_net`, `rio_add_device/del_device`, `rio_request/release_inb_mbox`, `rio_request/release_outb_mbox`, `rio_request/release_inb_dbell`, `rio_request/release_outb_dbell`, `rio_add/del_mport_pw_handler`, `rio_request/release_inb_pwrite`, `rio_pw_enable`, `rio_map/unmap_inb_region`, `rio_map/unmap_outb_region`, `rio_mport_get_physefb`, `rio_mport_get_efb`, `rio_mport_get_feature`, `rio_lock/unlock_device`, `rio_route_add/get/clr_table`, optional `rio_request_mport_dma`, `rio_dma_prep_xfer`, `rio_register_scan`, `rio_mport_scan`, `rio_init_mports`, `rio_mport_initialize`, `rio_register_mport`, and `rio_unregister_mport`.

## Control flow
Mport drivers initialize and register master ports; scan ops attach by exact mport ID or `RIO_MPORT_ANY`. Scans run enumeration if `host_deviceid >= 0`, otherwise discovery. Device and network add/remove paths register Linux devices and maintain global/per-net lists under spinlocks. Mailbox/doorbell request paths allocate `struct resource`, reserve the corresponding resource tree, attach callbacks, and call mport driver open/close hooks. Route operations optionally take the RapidIO host lock, then serialize on the switch lock, prefer switch-specific `rio_switch_ops`, and fall back to standard RapidIO route CSRs. Port-write handling resolves component tags, invokes per-device and per-mport callbacks, traces failed routes if the sender is inaccessible, performs switch error handling, toggles lockout on insertion/removal, clears ack/error status, and clears EM detect registers. Mport unregister transitions state, removes child devices, frees the net, removes the mport from the registry, and unregisters the device.

## State and persistence
Core state is in kernel lists, Linux resources, callbacks, refcounts, mport state, switch route caches, and hardware CSRs. Module parameter `hdid[]` supplies host destID assignment. Hardware-persistent actions include mailbox/doorbell setup by mport drivers, port-write enablement, route table writes, lockout bits, ack status updates, and memory window mappings.

## Dependencies and integration
Integrates with `linux/rio.h`, `rio_drv.h`, mport operation tables, RapidIO bus/classes, switch drivers, DMAEngine when enabled, Linux resources, workqueues, and module reference management through `try_module_get()` around scan and switch ops.

## Risks
Some legacy APIs return generic `-1` instead of errno. Several hardware access paths assume successful config reads. Port-write recovery is partly generic and explicitly not universal for all switches. Resource callback arrays are indexed by caller-supplied mailbox IDs and rely on upper-layer validation. The scan workqueue holds the mport list mutex while flushing discovery work, which deserves deadlock scrutiny if callbacks re-enter mport registration paths.

## Test signals
Validate mailbox/doorbell resource conflicts and cleanup, mport scan registration precedence, enumeration/discovery dispatch, switch-specific and standard route ops, port-write insertion/removal/error-stopped recovery, mport unregister cleanup of child devices and nets, DMAEngine wrappers under `CONFIG_RAPIDIO_DMA_ENGINE`, and behavior with absent mport operations.
