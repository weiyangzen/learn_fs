# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ppc-pci.h

Purpose: This header collects generic PowerPC PCI declarations spanning host bridges, ISA bridge state, device-tree traversal, RTAS PCI configuration, IOMMU registration, EEH, and optional ULI1575 initialization.

Important APIs/types/functions: It declares `isa_io_base`, `hose_list`, `isa_bridge_pcidev`, `BUID_HI`, `BUID_LO`, `pci_traverse_device_nodes`, `pci_devs_phb_init_dynamic`, optional `ppc_iommu_register_device` and unregister stubs, RTAS helpers `init_pci_config_tokens`, `get_phb_buid`, `rtas_setup_phb`, config accessors `rtas_pci_dn_read_config` and write, EEH cache/state/sysfs helpers, `uli_init`, and `PCI_BUSNO`.

Control flow: PCI initialization sets config tokens, discovers PHBs, initializes device nodes, registers IOMMU devices when pseries/PowerNV IOMMU API is available, and sets up RTAS-backed config access. EEH code inserts/removes devices from address caches, marks or clears PE states, resets PEs, saves BARs, and updates sysfs.

State and persistence: The header references global PCI topology state: host bridge lists, ISA bridge pointer, EEH caches, IOMMU registration, and per-PHB/device-node metadata. It defines no storage itself.

Dependencies and integration points: It is gated by `CONFIG_PCI` and includes Linux PCI plus `asm/pci-bridge.h`. It integrates PowerPC PCI host bridge code with Open Firmware nodes, RTAS calls, IOMMU API, EEH error recovery, sysfs, and Freescale ULI1575 support.

Risks and test signals: Config-dependent stubs must preserve buildability when PCI or IOMMU is disabled. RTAS config access must use the correct `pci_dn` and size. EEH state transitions can affect recovery and device removal. Tests should cover PCI boot enumeration, dynamic PHB init, RTAS config reads/writes, EEH injection/recovery, IOMMU add/remove, and no-PCI builds.
