# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/xenbus.c

## Purpose
`xenbus.c` is the Xenbus backend driver for `xen-backend:pci`. It creates `xen_pcibk_device` instances, reads toolstack-provided PCI BDFs, exports pcistub-owned devices to a frontend, publishes guest-visible roots/devices in Xenstore, maps the pcifront shared page, binds the event channel, and drives Xenbus state transitions.

## Important APIs, Types, And Functions
Key lifecycle functions are `alloc_pdev()`, `free_pdev()`, `xen_pcibk_xenbus_probe()`, and `xen_pcibk_xenbus_remove()`. Connection setup is split across `xen_pcibk_setup_backend()`, `xen_pcibk_attach()`, and `xen_pcibk_do_attach()`. Device publication/removal uses `xen_pcibk_export_device()`, `xen_pcibk_remove_device()`, `xen_pcibk_publish_pci_dev()`, and `xen_pcibk_publish_pci_root()`. Hotplug/reconfigure is handled by `xen_pcibk_reconfigure()` and `xen_pcibk_be_watch()`.

## Control Flow
Probe allocates the backend instance, initializes the selected topology backend, switches to `InitWait`, registers a watch on its backend node, and immediately invokes the watch. Backend setup reads `num_devs` and `dev-N`, gets each physical device from pcistub, adds it to the topology backend, marks `state-N` as `Initialised`, publishes PCI roots, and moves to `Initialised`. Once the frontend reaches `Initialised`, `xen_pcibk_attach()` reads `pci-op-ref`, `event-channel`, and `magic`, maps the shared page, binds a late-EOI interdomain IRQ to `xen_pcibk_handle_event()`, and switches to `Connected`. Reconfigure processes per-device substates for add/remove and moves to `Reconfigured`. Closing/closed states disconnect the ring/event channel and may unregister the device.

## State And Persistence
Per-instance state is in `xen_pcibk_device`: mapped shared info, event IRQ, backend watch, dev mutex, and topology mapping data. Xenstore stores `num_devs`, `dev-N`, `vdev-N`, `state-N`, `root-N`, `root_num`, frontend event-channel/grant reference, and driver state. The module parameter `passthrough` selects `vpci` or passthrough topology at registration.

## Dependencies And Integration Points
This file depends on Xenbus, Xen events, grant mapping, Xen PCI ownership helpers, pcistub ownership, `pciback_ops.c` event handling, and the topology backend callback table. It registers via `xenbus_register_backend()`.

## Risks
Risks include mismatched frontend `XEN_PCI_MAGIC`, partial Xenstore reconfiguration, device ownership stealing from another domain, leaking mapped rings on attach failure, hot-remove while operations are active, and state-machine divergence between backend and frontend. The code relies on `dev_lock` and workqueue flushing to serialize disconnect with request processing.

## Test Signals
Check Xenstore state progression `InitWait -> Initialised -> Connected`, successful guest pci enumeration, reconfigure add/remove transitions, clean close with unmapped ring and unbound IRQ, and logs for root/vdev publication and backend selection.
