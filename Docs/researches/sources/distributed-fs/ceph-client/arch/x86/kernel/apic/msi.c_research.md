# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/msi.c

## Purpose
This file implements x86 APIC-backed MSI domain support for PCI MSI/MSI-X, DMAR/IOMMU MSI, and Xen MSI restore integration. It connects MSI allocation and affinity changes to the x86 vector domain and APIC message composition.

## Important APIs, Types, And Functions
`x86_pci_msi_default_domain` stores the default PCI MSI parent domain. `irq_msi_update_msg()` composes and writes an MSI message. `msi_set_affinity()` migrates MSI targets safely. `pci_dev_has_default_msi_parent_domain()` checks whether a PCI device uses the vector domain. `x86_msi_prepare()` initializes x86 allocation info for MSI/MSI-X. `x86_init_dev_msi_info()` configures child MSI domain info based on the real parent. `native_create_pci_msi_domain()` marks `x86_vector_domain` as an MSI parent, and `x86_create_pci_msi_domain()` invokes platform creation. Legacy exported `pci_msi_prepare()` remains for Hyper-V. DMAR support defines `dmar_msi_controller`, domain ops, `dmar_alloc_hwirq()`, and `dmar_free_hwirq()`.

## Control Flow
During initialization, the vector domain becomes an MSI parent and platform code creates the default PCI MSI domain. Device MSI allocation calls `x86_msi_prepare()` to set allocation type, then parent vector allocation assigns vectors and destination APIC IDs. Affinity changes call `msi_set_affinity()`, which asks the parent vector chip for a new target and rewrites MSI messages. For non-maskable non-remapped MSI moves with changed vector and CPU, it temporarily redirects to the new vector on the current CPU under `vector_lock`, then moves to the final CPU and retriggers if the local LAPIC IRR shows a raced interrupt.

## State And Persistence
The file persists the default MSI domain pointer and lazily creates a singleton DMAR MSI domain protected by a mutex. Per-interrupt state lives in parent `irq_cfg` and generic MSI descriptors.

## Dependencies And Integration Points
It depends on the vector domain, `__irq_msi_compose_msg()` from `apic.c`, IRQ remapping parent domains, PCI/MSI core, DMAR APIs, Xen initdom restore, and vector move helpers. DMAR composition uses high destination APIC ID bits specially.

## Risks
MSI address/data updates are not always atomic, so affinity migration can create rare stray interrupts; the local temporary-vector path mitigates this. Incorrect feature flag filtering can expose unsupported MSI domain capabilities. DMAR high-address destination encoding must not be used for ordinary MSI devices.

## Test Signals
Validate PCI MSI/MSI-X allocation, affinity changes under load, vector migration races, interrupt remapping on/off, DMAR fault interrupt allocation, Xen initial-domain MSI restore, and devices with/without maskable MSI support.
