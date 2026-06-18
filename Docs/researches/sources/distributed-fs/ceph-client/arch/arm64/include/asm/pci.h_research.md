# sources/distributed-fs/ceph-client/arch/arm64/include/asm/pci.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pci.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/pci.h

### Purpose
`pci.h` provides ARM64 PCI architecture policy and includes generic PCI support.

### Important APIs, Types, And Functions
It defines `PCIBIOS_MIN_IO`, `pcibios_assign_all_busses()`, `arch_can_pci_mmap_wc()`, includes DMA mapping/I/O helpers, and delegates most behavior to `asm-generic/pci.h`.

### Control Flow
PCI core uses these macros during bus/resource setup and mmap validation. Device drivers use the generic PCI APIs backed by this architecture policy.

### State, Persistence, And Dependencies
PCI state lives in device/resource structures and DMA mappings. Dependencies include `linux/dma-mapping.h`, `asm/io.h`, and generic PCI.

### Integration Points
Affects network/storage adapters used by distributed filesystems and Ceph deployments.

### Risks
Resource window policy or write-combine mmap support must match platform capabilities. DMA mapping assumptions must stay coherent with IOMMU/cache behavior.

### Test Signals
Boot PCIe ARM64 systems, enumerate devices, test WC mmaps, DMA, IOMMU, and hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/pci.h -->
