# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/pci_dlpar.c

Purpose: Handles dynamic add/remove of pSeries PCI host bridges for DLPAR/hotplug flows.

Important APIs/types/functions: Exports `init_phb_dynamic()` and `remove_phb_dynamic()`.

Control flow: Add initializes NUMA node state for the PHB node, allocates a `pci_controller`, sets up RTAS ranges/controller ops, initializes pci_dn data, MSI domains, IOMMU registration, EEH PE structures, scans the PHB, and finishes bus addition. Remove requires an empty root bus, unmaps I/O space, unregisters IOMMU/MSI, removes the bus and host bridge device, and releases I/O and memory resources while relying on deferred controller freeing.

State and persistence: State lives in the dynamically allocated `pci_controller`, PCI bus/device tree objects, MSI domains, IOMMU registration, EEH PE records, and node online state.

Dependencies and integration points: Integrates with PCI core, pseries RTAS PHB setup, pseries MSI, ppc IOMMU, EEH, NUMA node registration, and `pseries_root_bridge_prepare()` deferred release.

Risks: Removal while child devices remain is refused, but lifetime is still delicate because bus removal, host bridge unregister, and deferred controller free must happen in the right order. Error paths in add are sparse because many helper failures are not explicitly unwound.

Test signals: PCI PHB hot-add/hot-remove, remove with active children returning `-EBUSY`, NUMA node creation, EEH device creation, MSI allocation/free, IOMMU registration cleanup, and repeated DLPAR cycles.

Source read size: 129 lines, 3557 bytes.
