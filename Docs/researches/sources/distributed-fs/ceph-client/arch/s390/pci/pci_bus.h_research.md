<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_bus.h -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_bus.h

Purpose: This private s390 PCI header exposes bus, device-registration, scan/remove, zdev reference, domain, and resource helpers shared by the zPCI implementation files.

Important APIs/types/functions: It declares `zpci_bus_device_register`, `zpci_bus_device_unregister`, `zpci_bus_scan_bus`, `zpci_bus_get_next`, `zpci_bus_scan_device`, `zpci_bus_remove_device`, `zpci_release_device`, `zpci_zdev_put`, `zpci_alloc_domain`, `zpci_free_domain`, and `zpci_setup_bus_resources`. Inline helpers are `zpci_zdev_get` for kref acquisition and `zdev_from_bus` for recovering the root zPCI device from `pci_bus->sysdata`.

Control flow: Discovery, event, and hotplug code include this header to move zPCI functions through allocation, registration, scanning, removal, and final kref release. The `zdev_from_bus` helper maps generic PCI bus callbacks back to the s390-specific bus/function table.

State and persistence: The header defines no storage, but its API contracts control lifetimes for `struct zpci_dev` and `struct zpci_bus`. Kref helpers make zdev references explicit and rely on `zpci_release_device` as the final release callback.

Dependencies and integration points: It depends on `asm/pci.h`/zPCI core definitions and generic PCI `struct pci_bus`. It connects `pci_bus.c` to CLP discovery, event handling, hotplug, resource setup, and PCI core callbacks.

Risks and test signals: Incorrect reference ownership around `zpci_zdev_get`/`zpci_zdev_put` can leak or prematurely free zdevs. Callers must not use `zdev_from_bus` on a bus whose `sysdata` is not a zPCI bus. Build coverage across PCI-enabled s390 configs and hotplug stress tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_bus.h -->
