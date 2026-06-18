<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_iov.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_iov.c

Purpose: This file provides s390-specific SR-IOV wiring for virtual functions whose platform representation is a zPCI function rather than a normal PCI-discovered child.

Important APIs/types/functions: Public helpers are `zpci_iov_map_resources`, `zpci_iov_remove_virtfn`, `zpci_iov_find_parent_pf`, and `zpci_iov_setup_virtfn`. Internal state includes the synthetic `iov_res` resource and `zpci_iov_link_virtfn`.

Control flow: Resource mapping replaces VF resources with offsets into a synthetic IOV resource window. During `pcibios_bus_add_device`, VFs call `zpci_iov_setup_virtfn`, which finds the parent PF by scanning the zbus function table for a physical function with matching FID parameter, links the VF into the PF's SR-IOV arrays, sets VF fields such as `is_virtfn`, `physfn`, and `no_command_memory`, and arranges sysfs links. Removal tears down the PF/VF relationship.

State and persistence: VF state persists in generic `struct pci_dev` fields and in zPCI metadata (`vfn`, `fidparm`, parent bus table). The synthetic IOV resource describes VF BAR ranges rather than firmware-owned BAR resources.

Dependencies and integration points: It depends on `CONFIG_PCI_IOV`, generic PCI SR-IOV structures, zPCI bus/function tables, sysfs PF/VF links, and s390 PCI BAR resource setup. It is called from bus add/remove code.

Risks and test signals: PF matching by FID parameter must not associate a VF with the wrong physical function. Refcounting on `physfn` and slot lookups must be balanced. Resource remapping must preserve VF BAR sizes and flags. Tests include PF with multiple VFs, isolated VF discovery before PF discovery, VF removal, sysfs virtfn links, driver binding to VFs, and no-IOV build coverage through header stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_iov.c -->
