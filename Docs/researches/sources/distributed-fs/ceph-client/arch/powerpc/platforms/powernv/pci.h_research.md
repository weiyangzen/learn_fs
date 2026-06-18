## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/pci.h

### Purpose
`pci.h` is the private PowerNV PCI/IODA header. It defines PHB and PE data structures, PE flag semantics, SR-IOV state, shared helper macros, and cross-file prototypes for `pci.c`, `pci-ioda.c`, `pci-ioda-tce.c`, EEH, and SR-IOV code.

### Important APIs, Types, And Functions
Important definitions include `enum pnv_phb_type`, `enum pnv_phb_model`, PE flags such as `PNV_IODA_PE_DEV`, `PNV_IODA_PE_BUS_ALL`, `PNV_IODA_PE_MASTER`, and `PNV_IODA_PE_VF`, `struct pnv_ioda_pe`, `struct pnv_phb`, optional `struct pnv_iov_data`, `pnv_pci_is_m64()`, `pnv_pci_is_m64_flags()`, PE logging macros, IOMMU level constants, and declarations for PE, DMA, TCE, PHB init, SR-IOV, and EEH helpers.

### Control Flow
As a header it has no runtime control flow, but it defines the contracts used by source files. `pci-ioda.c` mutates `pnv_phb.ioda` state across init, PE allocation, DMA setup, and release. `pci-sriov.c` uses `pnv_iov_data` stored in `pdev->dev.archdata.iov_data`. `pci-ioda-tce.c` implements the TCE prototypes declared here.

### State, Persistence, And Dependencies
`struct pnv_phb` persists controller, OPAL ID, register mapping, MSI bitmap, diagnostic buffer, PE arrays, segment maps, reverse maps, and callback pointers. `struct pnv_ioda_pe` persists PE association and IOMMU group/table state. Dependencies include Linux IOMMU, MSI bitmap, PCI resource structures, and PowerPC PCI controller objects.

### Integration Points
All PowerNV PCI implementation files in this group include this header. It is not a public UAPI but is the internal ABI between PHB initialization, config access, DMA/TCE management, EEH, and SR-IOV support.

### Risks
Structure fields encode invariants not enforced by the type system: exactly one of device/bus/VF ownership, balanced `device_count`, valid PE reverse maps, consistent segment maps, and stable table group references. `pnv_pci_is_m64()` intentionally tests addresses rather than flags because PCI allocation can place 64-bit BARs in 32-bit windows.

### Test Signals
Compile coverage across `CONFIG_PCI_IOV`, `CONFIG_IOMMU_API`, and debugfs variants is important. Runtime tests should validate PE flags, M64 detection by address, SR-IOV archdata lifetime, table group declarations, and cross-file prototypes after API changes.
