# Research: sources/distributed-fs/ceph-client/include/linux/pci-epc.h

Purpose: `pci-epc.h` defines the PCI Endpoint Controller core interface: controller objects, operations, memory windows, BAR capabilities, feature discovery, endpoint-function attachment, BAR/MSI/MSI-X programming, address mapping, link control, and endpoint memory allocation.

Important APIs/types/functions: key types include `enum pci_epc_interface_type`, `struct pci_epc_map`, `struct pci_epc_ops`, `struct pci_epc_mem_window`, `struct pci_epc_mem`, `struct pci_epc`, `enum pci_epc_bar_type`, reserved BAR region descriptors, and `struct pci_epc_features`. APIs include `pci_epc_create()`/devm create, destroy, add/remove EPF, link notifications, init/deinit/bus-master notifications, write header, set/clear BAR, map/unmap address, set/get MSI/MSI-X, raise IRQ, map MSI IRQ, start/stop link, get features, free-BAR selection, get/put EPC by name, and EPC memory init/alloc/map/unmap helpers.

Control flow and state: an EPC driver registers an EPC with an ops table and memory windows. EPF drivers bind functions, request BAR and interrupt setup, map endpoint memory to RC PCI addresses, and start link operation. `struct pci_epc` maintains EPF lists, locks, function number bitmap, domain, configfs group, feature arrays, and initialization state. Memory allocation uses bitmap-managed windows protected by mutexes.

Dependencies and integration points: depends on `pci-epf.h`, device model, configfs, endpoint core implementation, PCI BAR constants, module ownership, and controller-specific iATU/window programming.

Risks and test signals: risks include ops called without required locking, BAR type misuse, incorrect inbound mapping alignment, memory-window bitmap leaks, MSI/MSI-X count mismatch, function/VF number conflicts, and notification ordering bugs. Tests should cover EPF bind/unbind, multi-function and VF assignment, BAR feature combinations, memory map/unmap, link up/down, interrupt raise paths, configfs lifecycle, and disabled endpoint builds.
