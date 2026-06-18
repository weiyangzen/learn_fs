# sources/distributed-fs/ceph-client/include/xen/interface/physdev.h

## Purpose
`physdev.h` defines Xen physical-device hypercall operations for IRQ EOI/status, I/O privilege setup, APIC access, PIRQ/MSI mapping, PCI device management, MSI-X preparation, PCI reset notification, and debug-port reset coordination.

## Important APIs, Types, and Functions
Key command families include `PHYSDEVOP_eoi`, `pirq_eoi_gmfn_v1/v2`, `irq_status_query`, `set_iopl`, `set_iobitmap`, `apic_read/write`, `alloc/free_irq_vector`, `map_pirq`, `unmap_pirq`, PCI add/remove/reset operations, `prepare_msix`, `release_msix`, and `dbgp_op`. Structures include `physdev_eoi`, `physdev_pirq_eoi_gmfn`, `physdev_irq_status_query`, `physdev_map_pirq`, `physdev_pci_device_add`, `physdev_pci_device`, and `pci_device_reset`.

## Control Flow
Privileged guests issue `physdev_op` with a command-specific struct. IRQ paths query whether EOI is required, register shared EOI bitmaps, and signal EOI after interrupt service. Device-management paths map GSIs/MSIs to PIRQs, announce PCI devices or removal, preserve MSI-X resources around assignment, and notify Xen after hardware reset.

## State and Persistence Behavior
The operations mutate Xen's IRQ routing, EOI tracking page, physical device ownership, MSI/PIRQ mappings, and cached PCI state. These are runtime hypervisor state tied to domains and physical devices.

## Dependencies and Integration Points
The header relies on Xen base types and is used by dom0/hardware-domain PCI, IRQ, APIC, and passthrough code. It interacts with Linux PCI reset paths, MSI/MSI-X setup, event channels, and interrupt controllers.

## Risks and Test Signals
Risks include stale PIRQ mappings, incorrect MSI segment/vector fields, mismatched v1/v2 EOI semantics, unsafe I/O privilege exposure, and failing to notify Xen after reset. Test signals include PCI passthrough attach/detach, MSI/MSI-X interrupt delivery, EOI bitmap behavior, APIC access checks, and reset mode coverage.
