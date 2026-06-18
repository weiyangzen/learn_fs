## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/pci.c

### Purpose
`pci.c` contains generic PowerNV PCI support shared by PHB implementations: slot/power helper exports, OPAL config-space access, EEH checks around config operations, PHB diagnostic data printing, controller shutdown, and platform PCI discovery.

### Important APIs, Types, And Functions
Exported functions include `pnv_pci_get_slot_id()`, `pnv_pci_get_device_tree()`, `pnv_pci_get_presence_state()`, `pnv_pci_get_power_state()`, `pnv_pci_set_power_state()`, `pnv_pci_dump_phb_diag_data()`, `pnv_pci_cfg_read()`, `pnv_pci_cfg_write()`, `pnv_pci_table_alloc()`, `pnv_pci_shutdown()`, and `pnv_pci_init()`. The file defines global `struct pci_ops pnv_pci_ops`.

### Control Flow
Slot helpers derive OPAL slot IDs from PHB DT nodes and BDFN or call OPAL for device tree/presence/power state. Config reads/writes translate `pci_dn` to OPAL PHB ID and BDFN, call byte/halfword/word OPAL config functions, and return PCI BIOS status. When EEH is enabled, reads detect all-ones failure values and call EEH failure checks; otherwise both reads/writes probe and clear OPAL frozen state when needed. Diagnostic printers decode P7IOC, PHB3, and PHB4 OPAL diagnostic structures and compact repeated PEST entries. `pnv_pci_init()` disables PCIe port services, initializes all compatible IODA/NPU PHBs, and installs IOMMU DMA ops.

### State, Persistence, And Dependencies
This file has little private state; it allocates IOMMU table structures and uses global hose lists/controller ops. Persistent state is in PHB firmware, PCI device state, and EEH status. Dependencies include OPAL PCI calls, PowerPC PCI DN structures, EEH, MSI/IOMMU headers, PHB-specific init functions, and generic PCI core flags.

### Integration Points
`powernv.h` declares `pnv_pci_init()` and `pnv_pci_shutdown()`. `pci-ioda.c` provides PHB-specific init and controller operations. External drivers can use exported slot and power-state helpers.

### Risks
Config read failures return all-ones values while still reporting `PCIBIOS_SUCCESSFUL`, relying on EEH/failure detection at higher layers. Power-state set returns `1` when an async message is copied, not just boolean success. Diagnostic printing must match firmware structure versions. PCIe port services are globally disabled due to platform/firmware assumptions.

### Test Signals
Test slot ID derivation for standard and NPU PHBs, missing OPAL tokens, async power-state setting, config accesses of all sizes, EEH frozen-state clearing, diagnostic buffer printing for each ioType, IOMMU table allocation initialization, PHB shutdown callbacks, and PCI init discovery of IODA2/IODA3/OpenCAPI nodes.
