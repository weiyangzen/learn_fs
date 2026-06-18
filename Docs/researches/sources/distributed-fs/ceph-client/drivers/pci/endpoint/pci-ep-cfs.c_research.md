<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-ep-cfs.c -->
# sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-ep-cfs.c

## Purpose
Provides the configfs control plane for PCI endpoint configuration. It creates `/config/pci_ep/functions` and `/config/pci_ep/controllers`, lets userspace instantiate endpoint functions, configure PCI header and interrupt fields, expose function-driver-specific attributes, link EPFs to primary or secondary EPC interfaces, associate virtual EPFs with physical EPFs, and start or stop endpoint controllers.

## Important APIs, Types, and Functions
`struct pci_epf_group` wraps a configfs group, primary/secondary EPC subgroups, the EPF pointer, and an IDR index. `struct pci_epc_group` wraps a controller configfs group, EPC pointer, and `start` state. Exported entry points are `pci_ep_cfs_add_epc_group()`, `pci_ep_cfs_remove_epc_group()`, `pci_ep_cfs_add_epf_group()`, and `pci_ep_cfs_remove_epf_group()`.

Key callbacks include primary/secondary link and unlink handlers, `pci_epc_start_store()`, `pci_epf_make()`, `pci_epf_release()`, `pci_epf_type_add_cfs()`, and virtual EPF link/unlink callbacks. Attribute macros generate configfs accessors for PCI header fields and MSI/MSI-X interrupt counts.

## Control Flow
Module init registers the `pci_ep` subsystem and default `functions` and `controllers` groups. EPC creation in controller drivers calls `pci_ep_cfs_add_epc_group()`, which registers a controller group and obtains an EPC reference by name. EPF driver registration creates a function-type group under `functions`; userspace creating an item under that group calls `pci_epf_make()`, allocates an ID, creates an EPF device, initializes primary and secondary subgroups, and asks the function driver for optional type-specific configfs groups.

Linking a function to a controller calls `pci_epc_add_epf()`, `pci_epf_bind()`, and `pci_epc_notify_pending_init()`. Unlink warns if the EPC is still started, calls `pci_epf_unbind()`, and removes the EPF from the EPC. Writing `start=1` calls `pci_epc_start()`; writing `start=0` calls `pci_epc_stop()`.

## State and Persistence
Configfs items are the persistent user-visible state while mounted, but all objects are in-kernel and disappear on item deletion/module unload. `functions_idr` gives stable instance suffixes for active EPFs only. Header fields and MSI/MSI-X counts are stored directly in the `struct pci_epf` and consumed by function drivers when binding and initializing the EPC. `epc_group->start` mirrors whether the configfs control plane started the controller.

## Dependencies and Integration Points
Depends on configfs, IDR, PCI EPF/EPC libraries, and optional function-driver `add_cfs()` callbacks. It is the integration point between userspace endpoint setup scripts, EPF function drivers, and EPC controller drivers. It relies on the EPF bus to bind `pci_epf_create()` devices to registered EPF drivers.

## Risks and Edge Cases
Several attributes can be written regardless of bind/start state; function drivers must decide which settings are safe after bind. Unlink only warns if a controller is started, so userspace sequencing matters. Type-specific configfs group creation requires the EPF to be driver-bound; errors are logged but the EPF instance may still exist with fewer controls. `pci_ep_cfs_remove_epf_group()` manipulates configfs group entries and must match groups created by EPF driver registration. Virtual EPF association requires both PF and VF to be unbound.

## Test Signals
Create/delete EPF instances for each function type, set header/MSI attributes, link primary and secondary EPCs, verify `pci_epf_bind()` failures roll back EPC association, start/stop controllers through configfs, associate/disassociate virtual EPFs, and unload EPF/EPC modules while configfs objects exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-ep-cfs.c -->
