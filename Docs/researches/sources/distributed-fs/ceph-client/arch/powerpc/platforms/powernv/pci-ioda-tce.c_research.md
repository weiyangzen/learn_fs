## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/pci-ioda-tce.c

### Purpose
`pci-ioda-tce.c` manages IODA2 TCE table allocation, multi-level lookup, build/free/exchange operations, userspace table copies, and links between IOMMU tables and PowerNV PE table groups.

### Important APIs, Types, And Functions
Important functions are `pnv_ioda_parse_tce_sizes()`, `pnv_pci_setup_iommu_table()`, `pnv_tce()`, `pnv_tce_build()`, `pnv_tce_xchg()`, `pnv_tce_useraddrptr()`, `pnv_tce_free()`, `pnv_tce_get()`, `pnv_pci_ioda2_table_alloc_pages()`, `pnv_pci_ioda2_table_free_pages()`, `pnv_pci_link_table_and_group()`, and `pnv_pci_unlink_table_and_group()`.

### Control Flow
Supported page sizes are read from `ibm,supported-tce-sizes`, with defaults based on CPU generation. Table allocation validates levels and power-of-two window size, computes per-level table sizes, allocates zeroed pages, optionally allocates a userspace mirror, and initializes `struct iommu_table`. `pnv_tce()` walks indirect levels, allocating lower levels atomically with `cmpxchg()` when requested. Build writes permission and real page number TCEs, free clears entries and skips missing lower levels, exchange atomically swaps one TCE, and free recursively releases allocated levels.

### State, Persistence, And Dependencies
State lives in `struct iommu_table`: base, offset, size, page shift, indirect level count, userspace mirror, NUMA node, and RCU-linked table groups. Hardware-visible persistence is the TCE table memory mapped into OPAL/PHB DMA windows by `pci-ioda.c`. Dependencies include PowerNV IOMMU constants, TCE permission helpers, OF properties, page allocator, RCU list links, and `iommu_tce_table_get/put()`.

### Integration Points
`pci-ioda.c` uses these helpers to create default and VFIO/userspace DMA windows, install table ops, invalidate PHB TCE caches after mutations, and manage table group ownership.

### Risks
Multi-level allocation uses `GFP_ATOMIC`, so memory pressure can fail DMA mapping. The direct allocation helper's partial-allocation handling is subtle for multi-level tables. Link/unlink functions assume matching table/group references and warn if not found. TCE entries encode pointers with read/write bits, so masking must be exact during recursive free and traversal.

### Test Signals
Test page-size property parsing, invalid levels/window sizes, single- and multi-level table allocation, userspace-copy allocation failure, concurrent lower-level allocation, build/free/xchg/get behavior, recursive free, RCU table/group linking, and VFIO table-size accounting.
