# sources/distributed-fs/ceph-client/kernel/irq/msi.c

## Purpose
`msi.c` is the generic Message Signaled Interrupt core for PCI and non-PCI devices. It manages per-device MSI descriptor stores, MSI irqdomains, per-device MSI domains, MSI message programming, allocation/free of Linux IRQs for MSI table entries, sysfs visibility, wired-to-MSI translation, and isolated-MSI capability detection.

## Important APIs, types, and functions
Important internal types are `struct msi_device_data`, storing per-device properties, a descriptor mutex, domain slots, xarrays, and iterator state, and `struct msi_ctrl`, describing domain/range/nirq operations. Public APIs include `msi_setup_device_data()`, `msi_domain_insert_msi_desc()`, `msi_domain_free_msi_descs_range()`, `msi_domain_first_desc()`, `msi_next_desc()`, `msi_domain_get_virq()`, `get_cached_msi_msg()`, `msi_create_irq_domain()`, `msi_create_parent_irq_domain()`, `msi_create_device_irq_domain()`, `msi_remove_device_irq_domain()`, `msi_match_device_irq_domain()`, `msi_domain_alloc_irqs_range()`, `msi_domain_alloc_irqs_all_locked()`, `msi_domain_alloc_irq_at()`, `msi_device_domain_alloc_wired()`, `msi_domain_free_irqs_range()`, `msi_domain_free_irqs_all()`, `msi_device_domain_free_wired()`, `msi_get_domain_info()`, `msi_device_has_isolated_msi()`, and `msi_domain_set_affinity()`.

## Control flow
Device setup allocates devres-managed MSI data, creates an optional `msi_irqs` sysfs group, initializes xarrays, and imports a legacy global MSI domain when present. Descriptor allocation inserts `msi_desc` objects by fixed or xarray-selected index. MSI domain creation fills default domain/chip ops, creates a hierarchical IRQ domain, applies bus tokens, and records domain metadata. Allocation prepares domain-specific alloc info, optionally creates simple descriptors, allocates IRQ descriptors through irqdomain hierarchy, associates each virq with the MSI descriptor, initializes/reserves/activates virqs, writes MSI messages on activation, and populates sysfs files. Freeing deactivates IRQs, frees irqdomain allocations, removes sysfs files, clears descriptor IRQs, and optionally frees descriptors.

## State and persistence
State is runtime-only and tied to `struct device`: xarray descriptor stores indexed by MSI table slot/domain id, per-device domain pointers, cached MSI messages in descriptors, sysfs attribute allocations, iterator position, and devres-owned domain/data cleanup. Hardware MSI table state is programmed via irqchip message writes and cleared on deactivation.

## Dependencies and integration points
This file integrates the generic IRQ domain hierarchy, `struct msi_domain_info` and `struct msi_domain_ops`, irqchip MSI message composition/writes, PCI MSI/MSI-X attributes, xarrays, devres, sysfs, cpumask affinity descriptors, device fwnodes, MSI parent domains, wire-to-MSI controllers, and architecture isolated-MSI policy.

## Risks and test signals
Risks include descriptor leaks when associated IRQs still exist, xarray index range errors, PCI multi-MSI fallback behavior, reservation-mode misuse on unmaskable devices, MSI message writes without level-capable support, per-device domain cleanup ordering, sysfs file lifetime, managed IRQ shutdown when no target CPU is online, and security assumptions around isolated MSI. Test signals include PCI MSI and MSI-X allocation/free, simple platform MSI descriptors, multi-domain devices, device removal with active descriptors, allocation failure rollback, reservation-mode activation, affinity changes rewriting messages, wired-to-MSI fwspec allocation, sysfs `msi_irqs` population/removal, and VFIO-style isolated-MSI checks.
