# sources/distributed-fs/ceph-client/drivers/pci/msi/legacy.c

## Purpose
Implements the legacy architecture-specific MSI setup and teardown path used when hierarchical MSI irqdomains are unavailable or disabled. It preserves weak arch hooks while adding generic descriptor/sysfs handling around them.

## APIs, Types, And Functions
Weak hooks are `arch_setup_msi_irq()`, `arch_teardown_msi_irq()`, `arch_setup_msi_irqs()`, and `arch_teardown_msi_irqs()`. PCI-facing helpers are `pci_msi_legacy_setup_msi_irqs()` and `pci_msi_legacy_teardown_msi_irqs()`. `pci_msi_setup_check_result()` converts partial MSI-X allocation failures into a positive available-vector count.

## Control Flow
The default `arch_setup_msi_irqs()` refuses multi-MSI for architectures that do not override it, then iterates unassociated descriptors and calls single-vector setup. Teardown iterates associated descriptors and tears down every used vector. The PCI wrapper normalizes partial MSI-X results and populates MSI sysfs entries after successful setup; teardown destroys those sysfs entries before invoking architecture teardown.

## State And Persistence
No persistent storage exists. State is held by MSI descriptors associated with the PCI device and by sysfs entries created by the generic MSI layer. Weak hooks are compile/link-time extension points.

## Dependencies And Integration
Depends on `msi.h`, generic descriptor iteration macros, and architecture-provided MSI setup implementations. `irqdomain.c` calls these helpers when no hierarchical domain is available; `msi.c` depends on them to allocate descriptor IRQ numbers in fallback mode.

## Risks And Test Signals
Risks are mostly compatibility-related: architectures returning positive retry counts, partial MSI-X allocation reporting, descriptor association state, and sysfs cleanup ordering. Test signals include booting on `CONFIG_PCI_MSI_ARCH_FALLBACKS` platforms, single MSI enablement, multi-MSI refusal without arch support, MSI-X partial allocation retry, and module/device removal leak checks.
