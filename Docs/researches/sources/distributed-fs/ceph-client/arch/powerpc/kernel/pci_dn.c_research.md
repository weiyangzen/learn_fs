# sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci_dn.c

Purpose: this file maintains PowerPC PCI firmware metadata (`struct pci_dn`) attached to Open Firmware device nodes and bridges it to Linux `pci_dev` objects. It also creates synthetic `pci_dn` and EEH metadata for SR-IOV virtual functions that do not have DT nodes.

Important APIs and functions: lookup helpers are `pci_get_pdn_by_devfn()` and `pci_get_pdn()`, backed by `pci_bus_to_pdn()`. SR-IOV support is provided by `add_sriov_vf_pdns()` and `remove_sriov_vf_pdns()`. `pci_add_device_node_info()` allocates and fills `pci_dn` fields from DT properties, initializes EEH state, and attaches the node to its parent child list. `pci_remove_device_node_info()` marks or frees `pci_dn` objects during dynamic node removal. `pci_traverse_device_nodes()` walks PCI-looking DT nodes depth first. `pci_devs_phb_init_dynamic()` initializes a PHB node and all child metadata. An early PCI fixup stores the resolved `pci_dn` in `pdev->dev.archdata.pci_data`.

Control flow: PHB initialization creates a root `pci_dn` with invalid bus/devfn, then traverses child nodes and allocates metadata for each device. PCI device creation or early fixup resolves fast-path archdata. Lookups first check live `pci_dev` archdata, then the device node, then the firmware child list. Dynamic removal detaches from parent lists, handles parent node references, and defers freeing if a matching `pci_dev` still exists. SR-IOV creation iterates total VFs and creates child-list entries with bus/devfn from PCI IOV helpers.

State and persistence: `dn->data` owns the pointer to `pci_dn`; parent/child lists model the PCI firmware hierarchy. Fields cache PHB pointer, bus number, devfn, vendor/device/class, extended config-space flag, PE number, flags, and optional EEH device. `PCI_DN_FLAG_DEAD` persists until `pcibios_release_device()` frees a metadata object after the PCI device release path is safe.

Dependencies and integration points: integrates with Open Firmware properties, EEH (`eeh_dev`, PE tree removal), PCI IOV helpers, `pci-hotplug.c` deferred release, `pci_of_scan.c` device creation, and PHB setup.

Risks: metadata lifetime is split between DT nodes and PCI devices, so removal order is critical. SR-IOV VF metadata is synthetic and must be kept consistent with PF total VFs and activated VF state. EEH cleanup must remove PE tree entries only when configured. Traversal uses class-code heuristics and can skip malformed firmware nodes.

Test signals: check that every scanned PCI device has `dev.archdata.pci_data`, dynamic PHB add/remove leaves no stale child-list entries, SR-IOV enable/disable creates and frees VF `pci_dn` plus EEH objects, and hotplug removal logs deferred dead pdn freeing without leaks or crashes.
