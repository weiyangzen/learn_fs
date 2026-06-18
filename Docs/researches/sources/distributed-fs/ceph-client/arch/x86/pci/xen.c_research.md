<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/xen.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/xen.c

## Purpose
`xen.c` replaces native x86 PCI INTx, ACPI GSI, and MSI/MSI-X setup with Xen PIRQ/event-channel based handling for PV guests, HVM guests needing PIRQs, and Xen initial domains. It bridges PCI core IRQ allocation to Xen hypercalls and frontend/backend operations.

## Important APIs, types, and functions
Key paths are `xen_pcifront_enable_irq()`, `xen_register_pirq()`, `acpi_register_gsi_xen_hvm()`, PV Dom0 `xen_register_gsi()`, MSI setup variants `xen_setup_msi_irqs()`, `xen_hvm_setup_msi_irqs()`, `xen_initdom_setup_msi_irqs()`, `xen_initdom_restore_msi()`, teardown helpers, the synthetic MSI irq-domain callbacks, `pci_xen_init()`, `pci_xen_hvm_init()`, and `pci_xen_initial_domain()`.

## Control flow
PV DomU installs pcifront INTx hooks and keeps ACPI out of IRQ routing. HVM installs ACPI GSI registration and defers MSI-domain replacement until APIC mode is known; if APIC virtualization is available, native MSI is retained. Initial domain installs MSI hypercall setup, ACPI GSI registration, and preallocates legacy IRQ overrides. MSI setup maps PCI devices or MSI-X table entries to Xen PIRQs, binds them to Linux IRQs, and populates MSI sysfs.

## State and persistence behavior
Global state includes exported `xen_pci_frontend`, `xen_msi_ops`, and `pci_seg_supported`. PCI device state is updated through `dev->irq`, MSI descriptors, and Xen IRQ bindings. Initial domain restore may switch permanently from segment-aware hypercalls to legacy calls if unsupported.

## Dependencies and integration points
It depends on Xen hypervisor feature flags, physdev operations, event-channel binding, pcifront MSI helpers, ACPI registration hooks, x86 APIC state, the MSI irq-domain framework, and generic PCI enable/disable flows.

## Risks and edge cases
Domain type determines which hooks are legal; using PV frontend ops in Dom0 or HVM paths would misroute interrupts. Multi-MSI support may return positive retry signals. MSI-X setup depends on a valid table BAR. Segment-aware hypercalls are probed and may degrade to legacy domain-0-only bus encoding. The synthetic irq domain is intentionally a compatibility wrapper.

## Test signals
Test PV DomU passthrough, HVM with and without APIC virtualization, PV Dom0, MSI and MSI-X devices, multi-MSI fallback, ACPI GSI overrides, suspend/resume MSI restore, and pcifront backend absence/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/xen.c -->
