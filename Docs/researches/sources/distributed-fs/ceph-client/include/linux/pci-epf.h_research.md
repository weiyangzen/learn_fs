# Research: sources/distributed-fs/ceph-client/include/linux/pci-epf.h

Purpose: `pci-epf.h` defines PCI Endpoint Function core objects and driver interfaces: endpoint function identity, config header, BARs, function driver callbacks, EPC event callbacks, virtual function support, MSI-X table metadata, and allocation/bind helpers.

Important APIs/types/functions: types include `enum pci_barno`, `struct pci_epf_header`, `struct pci_epf_ops`, `struct pci_epc_event_ops`, `struct pci_epf_driver`, `struct pci_epf_bar_submap`, `struct pci_epf_bar`, `struct pci_epf_doorbell_msg`, `struct pci_epf`, and `struct pci_epf_msix_tbl`. APIs include EPF create/destroy, driver register/unregister, BAR space allocation/free/assignment, inbound address alignment, bind/unbind, and virtual EPF add/remove.

Control flow and state: endpoint function drivers register an EPF driver, get probed for EPF devices, fill header/BAR/interrupt requirements, bind to an EPC, allocate BAR space, and react to EPC events such as init, link up/down, and bus master enable. `struct pci_epf` stores primary/secondary EPC association, BAR arrays for both, function numbers, driver/id pointers, configfs group, bound/VF state, VF bitmap/list, event ops, and doorbell messages.

Dependencies and integration points: depends on configfs, device model, module device tables, MSI, PCI core, and EPC features from `pci-epc.h`. It integrates with endpoint configfs, test functions, NTB/function drivers, and controller-specific EPC operations.

Risks and test signals: risks include BAR memory leaks, binding state races, secondary EPC inconsistencies, VF bitmap conflicts, invalid MSI-X table layout, and missing unbind cleanup. Tests should cover EPF driver probe/remove, configfs-created functions, BAR allocation alignment, subrange mappings, bind/unbind idempotence, virtual functions, and endpoint interrupt paths.
