<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-epf-core.c -->
# sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-epf-core.c

## Purpose
Provides the PCI endpoint function bus and helper library. It creates EPF devices, registers EPF drivers, binds/unbinds functions to EPCs, associates virtual functions with physical functions, allocates/assigns/free BAR backing memory, and exposes EPF driver configfs groups.

## Important APIs, Types, and Functions
Key exported APIs are `pci_epf_bind()`, `pci_epf_unbind()`, `pci_epf_add_vepf()`, `pci_epf_remove_vepf()`, `pci_epf_alloc_space()`, `pci_epf_assign_bar_space()`, `pci_epf_free_space()`, `pci_epf_register_driver()` via `__pci_epf_register_driver()`, `pci_epf_unregister_driver()`, `pci_epf_create()`, `pci_epf_destroy()`, and `pci_epf_align_inbound_addr()`. Bus callbacks match EPF devices by `pci_epf_device_id` or driver name and invoke driver probe/remove.

## Control Flow
Module init registers the `pci-epf` bus. Configfs creates EPF devices with names like `pci_epf_test.0`; `pci_epf_create()` stores the function type before the dot, initializes locks and VF tracking, and adds the device to the EPF bus. Driver registration validates bind/unbind ops, registers the driver, and creates configfs groups for each ID table entry. Binding first validates all associated VFs against EPC limits, binds VFs, then binds the PF and marks instances bound. Unbind calls VF unbinds then PF unbind and releases the driver module reference.

BAR allocation computes required BAR size based on EPC feature constraints, allocates coherent DMA memory from the EPC parent, and fills `struct pci_epf_bar`. Assignment is used for pre-existing physical ranges such as MSI doorbell message pages. Free releases coherent memory and clears BAR metadata.

## State and Persistence
State lives in `struct pci_epf`: name, device, driver, header, BAR arrays, EPC pointers, function/VF numbers, VF list, bound flags, configfs group, and event ops set by function drivers. Configfs groups for function types are tracked in each EPF driver and removed at unregister.

## Dependencies and Integration Points
Depends on the driver core, DMA coherent allocation, endpoint configfs, and EPC feature descriptions. It connects configfs-created EPF devices to function drivers such as `pci_epf_test` and `pci_epf_vntb`.

## Risks and Edge Cases
`pci_epf_bind()` calls `pci_epf_unbind()` on error, so partial VF/PF binds must tolerate cleanup. VF numbering reserves bit 0 because VFs start at 1. `pci_epf_add_vepf()` rejects association after either side is EPC-bound. BAR allocation assumes valid EPC pointers for the selected interface. `pci_epf_align_inbound_addr()` aligns to current BAR size and assumes power-of-two BAR sizes.

## Test Signals
Create EPFs before/after driver registration, bind/unbind PFs and VFs, test VF limits from EPC features, allocate fixed/resizable/64-bit BARs, assign BARs to unaligned physical addresses, unload EPF drivers with live configfs groups, and verify driver probe/remove matching by ID table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-epf-core.c -->
