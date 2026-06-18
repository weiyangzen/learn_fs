<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-epc-core.c -->
# sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-epc-core.c

## Purpose
Provides the core library and class for PCI endpoint controllers. It registers EPC devices, exposes controller operations to endpoint functions, validates function/VF numbers, serializes controller callbacks, manages EPF attachment, delivers link/init/bus-master notifications, and adds EPCs to endpoint configfs.

## Important APIs, Types, and Functions
Key exported APIs include `pci_epc_get()/put()`, `pci_epc_get_features()`, `pci_epc_start()/stop()`, `pci_epc_raise_irq()`, `pci_epc_set_msi()/get_msi()`, `pci_epc_set_msix()/get_msix()`, `pci_epc_map_addr()/unmap_addr()`, `pci_epc_mem_map()/mem_unmap()`, `pci_epc_set_bar()/clear_bar()`, `pci_epc_write_header()`, `pci_epc_add_epf()/remove_epf()`, notification helpers, `__pci_epc_create()`, and `__devm_pci_epc_create()`.

## Control Flow
Module init registers the `pci_epc` class. Controller drivers create EPC objects with operation tables; creation initializes locks, the EPF list, class device, domain number, and configfs group. EPF configfs linking calls `pci_epc_add_epf()`, which allocates a function number and links the EPF into the controller list. EPF drivers then call exported wrappers; each wrapper validates function numbers and operation presence before locking `epc->lock` and invoking controller-specific callbacks.

Notifications walk the attached EPF list under `list_lock`, take each EPF lock, and call optional event ops for link up/down, EPC init/deinit, or bus master enable. `pci_epc_mem_map()` combines endpoint memory allocation, optional controller address alignment, and outbound mapping into one temporary host-PCI mapping used by test/data drivers.

## State and Persistence
EPC state includes class device lifetime, operation table, parent device, domain number, max functions/VFs, attached EPF list, function-number bitmap, configfs group, memory windows, and `init_complete`. The library persists only in-kernel state. References are managed through class device lookup and module owner counts.

## Dependencies and Integration Points
Depends on the Linux driver core, PCI endpoint function headers, endpoint configfs, domain-number helpers, and EPC controller operation implementations. It is the central integration point between hardware-specific EPC drivers, EPF function drivers, and configfs.

## Risks and Edge Cases
All wrappers return success when an optional operation is missing in several cases, so callers must know whether a no-op is acceptable. Function number allocation is limited by `BITS_PER_LONG` and `epc->max_functions`. `pci_epc_set_bar()` enforces power-of-two size, fixed/resizable BAR constraints, 64-bit BAR legality, and submap feature support; callers that mutate `struct pci_epf_bar` must keep it internally consistent. Notification callbacks run under EPC list locking and EPF locking, so callback reentrancy into configfs/link paths must be considered. `pci_epc_get()` calls `put_device(dev)` even on the error path where `dev` may be NULL; this relies on `put_device(NULL)` safety.

## Test Signals
Create/destroy EPC devices, link multiple EPFs until function limits, exercise all wrappers with missing and present ops, validate BAR error paths, test init notification before and after EPF bind, test VF validation, run endpoint-test transfers using `pci_epc_mem_map()`, and unload controller modules while references/configfs groups exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-epc-core.c -->
