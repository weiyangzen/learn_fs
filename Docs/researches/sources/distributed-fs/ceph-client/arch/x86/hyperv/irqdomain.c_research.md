## `sources/distributed-fs/ceph-client/arch/x86/hyperv/irqdomain.c`

Purpose: implements IRQ and MSI mapping for Linux running as the Hyper-V root partition, translating Linux IRQ affinity/vector choices into Microsoft Hypervisor device-interrupt mappings.

Important APIs and functions: `hv_map_interrupt()` and `hv_unmap_interrupt()` issue core map/unmap hypercalls. Exported wrappers include `hv_map_msi_interrupt()`, `hv_map_ioapic_interrupt()`, and `hv_unmap_ioapic_interrupt()`. PCI MSI support includes `hv_build_pci_dev_id()`, `hv_irq_compose_msi_msg()`, `hv_teardown_msi_irq()`, `hv_create_pci_msi_domain()`, and MSI parent/domain ops.

Control flow: mapping builds a device ID, fixed interrupt descriptor, target vector, trigger mode, and sparse VP set for the target CPU, then performs `HVCALL_MAP_DEVICE_INTERRUPT`. MSI compose unmaps any previous entry because retargeting cannot change vector or outside-VP set, maps a fresh entry, stores it in `irq_data.chip_data`, and converts the returned Hyper-V entry to `struct msi_msg`. Free tears down stored mappings.

State and persistence: per-IRQ `chip_data` stores the Hyper-V interrupt entry needed for unmap. The created MSI domain persists for the root partition. Hypervisor mapping state persists until explicitly unmapped.

Dependencies and integration points: PCI/MSI core, x86 vector domain, Hyper-V current partition ID, per-CPU hypercall buffers, VP-set helpers, IRQ affinity, and IOAPIC routing.

Risks: stale `chip_data` or missed unmap leaks hypervisor mappings. PCI alias/PCI-X bridge shadow bus range handling is required for correct device IDs. Domain free currently gets irq data using `virq` in the loop, a detail worth regression scrutiny for multi-IRQ frees.

Test signals: PCI MSI/MSI-X devices in root partition, IRQ affinity changes, device remove/reprobe, IOAPIC interrupt mapping, and hypercall error logging.
