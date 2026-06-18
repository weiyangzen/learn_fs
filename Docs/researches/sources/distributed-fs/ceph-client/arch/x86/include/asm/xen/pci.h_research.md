<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/pci.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/pci.h

Purpose: Declares Xen-specific PCI initialization and PCI frontend MSI/MSI-X hooks, with no-op or error stubs when the relevant Xen PCI options are disabled.

Important APIs/types/functions: `pci_xen_init()`, `pci_xen_hvm_init()`, `pci_xen_initial_domain()`, `pci_xen`, `struct xen_pci_frontend_ops`, `xen_pci_frontend`, and inline wrappers for frontend MSI/MSI-X enable/disable.

Control flow: PCI setup calls Xen init hooks based on configuration and domain type. MSI/MSI-X wrappers check whether `xen_pci_frontend` and its operation are installed, delegate when present, and return `-ENOSYS` or no-op otherwise.

State and persistence behavior: Persistent state is the global `xen_pci_frontend` operations pointer provided by Xen PCI frontend code. PCI device MSI state is mutated by the delegated operations.

Dependencies and integration points: Integrates with `CONFIG_PCI_XEN`, `CONFIG_XEN_PV_DOM0`, `CONFIG_PCI_MSI`, PCI device setup, Xen pcifront, HVM PCI initialization, and dom0 PCI ownership.

Risks and test signals: Risks include missing frontend ops, stubs compiled into unexpected configs, and MSI vector leakage during frontend failure paths. Test Xen dom0 and domU PCI probing, MSI/MSI-X enable and disable, HVM guest PCI init, pcifront load/unload, and non-Xen PCI builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/pci.h -->
