# sources/distributed-fs/ceph-client/arch/s390/include/asm/pci.h

Purpose: This is the central s390 zPCI header, defining PCI mapping hooks, zPCI function/bus state, measurement blocks, hotplug/sysfs/IOMMU/DMA/IRQ/debug prototypes, and device helper conversions.

Important APIs/types/functions: It defines PCI min windows, zPCI device/domain constants, function-control bits, FMB formats, `enum zpci_state`, `struct zpci_bar_struct`, `struct zpci_bus`, `struct zpci_dev`, `zdev_enabled()`, sysfs attribute groups, globals such as `zpci_aipb`, and a broad API for create/add/enable/disable/scan/deconfigure/reset, CLP operations, UID checking, firmware sysfs, IOMMU, hotplug, DMA, IRQ/MSI, FMB, debug, and error reporting.

Control flow: Firmware discovery scans CLP-provided functions, creates `zpci_dev` objects, queries function/group attributes, enables functions to obtain handles, registers I/O address translation, maps BAR resources, initializes IOMMU/MSI/debug/hotplug state, and handles availability/error events for recovery or deconfiguration.

State and persistence: Persistent state is large per zPCI function and bus: krefs/RCU/list membership, state locks, firmware IDs/handles, RID/topology/PFIP/UID, BAR mapping pointers, MSI vectors and adapter interrupt bit vectors, DMA table and address limits, IOMMU domain/device, FMB counters, debugfs entries, KVM passthrough pointer, and hotplug slot state.

Dependencies and integration points: It depends on Linux PCI, IOMMU, IRQ domains, hotplug, CLP records, zPCI instruction helpers, SCLP, debug, and KVM zPCI hooks.

Risks and test signals: State transitions must be serialized because firmware handles, DMA windows, MSI routing, and hotplug removal interact. Tests should cover CLP scan, enable/disable/re-enable, BAR mmap/iomap, DMA map/unmap, MSI delivery, FMB counters, hotplug, error recovery, IOMMU attach/detach, and passthrough.
