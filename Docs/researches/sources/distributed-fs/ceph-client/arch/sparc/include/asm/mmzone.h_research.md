# sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmzone.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmzone.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmzone.h` connects SPARC NUMA builds to generic memory-zone declarations or disables architecture NUMA hooks when NUMA is off. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 14 lines, 280 bytes. Primary surface: `NODE_DATA`, `pa_to_nid`, `pfn_to_nid`, or generic `mmzone.h` inclusion depending on config. Symbol scan highlights: `_SPARC64_MMZONE_H`.

### Control Flow
MM code maps physical addresses/PFNs to NUMA nodes only when NUMA support is enabled. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
node data lives in generic/architecture NUMA initialization. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/cpumask.h>`. Integration dependencies: `CONFIG_NEED_MULTIPLE_NODES`, generic MM zone code, and SPARC NUMA setup.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong node mapping can allocate memory from invalid zones or break page accounting.

### Test Signals
NUMA and non-NUMA SPARC64 builds, page allocator tests, and memory hotplug/topology checks. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
