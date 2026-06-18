# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/passthrough.c

## Purpose
`passthrough.c` implements the pciback backend mode that exposes PCI devices to the frontend using their real host domain/bus/devfn topology rather than virtualized BDF numbering.

## Important APIs, types, and functions
The key local type is `struct passthrough_dev_data`, containing a device list and mutex. Backend callbacks are implemented by `__xen_pcibk_init_devices`, `__xen_pcibk_add_pci_dev`, `__xen_pcibk_get_pci_dev`, `__xen_pcibk_publish_pci_roots`, `__xen_pcibk_release_pci_dev`, `__xen_pcibk_release_devices`, and `__xen_pcibk_get_pcifront_dev`. They are published through `xen_pcibk_passthrough_backend`.

## Control flow
Backend init allocates the list container. Adding a PCI device appends it to the protected list and publishes its real domain/bus/devfn through the provided callback. Lookup scans the list for the requested BDF. Publishing roots walks exported devices and publishes only those whose parent bridges are not also exported. Release removes entries and returns devices to pcistub. Full teardown releases every tracked device and frees backend data.

## State and persistence
State is a per-`xen_pcibk_device` list of exported `pci_dev` pointers protected by a mutex. Device ownership is returned to pcistub on release. No state persists beyond backend lifetime.

## Dependencies and integration points
It depends on Linux PCI structures, pciback backend callback definitions, and pcistub get/put ownership. It integrates with xenbus publishing and pciback operation paths via `xen_pcibk_backend`.

## Risks and test signals
Risks include duplicate devices, publishing incorrect roots when parent bridges are also exported, locking around device release, stale `pci_dev` pointers, and frontend requests for unexported BDFs. Test signals include passthrough mode with single devices and bridge hierarchies, add/release cycles, lookup for missing devices, frontend AER mapping, and concurrent publish/release behavior.
