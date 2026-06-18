# sources/distributed-fs/ceph-client/arch/sparc/include/asm/io-unit.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/io-unit.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/io-unit.h` defines the SPARC32 IO-UNIT DVMA window, IOPTE bits, and allocator state for legacy SBus/IO-UNIT DMA mappings. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 59 lines, 2469 bytes. Primary surface: `IOUNIT_DMA_BASE`, `IOUNIT_DMA_SIZE`, `IOUNIT_DVMA_SIZE`, `IOUPTE_*`, `struct iounit_struct`, and bitmap range constants. Symbol scan highlights: `_SPARC_IO_UNIT_H`, `IOUNIT_DMA_BASE`, `IOUNIT_DMA_SIZE`, `IOUNIT_DVMA_SIZE`, `IOUPTE_PAGE`, `IOUPTE_CACHE`, `IOUPTE_STREAM`, `IOUPTE_INTRA`, `IOUPTE_WRITE`, `IOUPTE_VALID`, `IOUPTE_PARITY`, `struct iounit_struct`, `IOUNIT_BMAP1_START`, `IOUNIT_BMAP1_END`, `IOUNIT_BMAP2_START`, `IOUNIT_BMAP2_END`, `IOUNIT_BMAPM_START`, `IOUNIT_BMAPM_END`.

### Control Flow
SBus DMA code allocates address ranges from `bmap`, fills `page_table` IOPTEs with physical page and permission/cache bits, and programs IO-UNIT translations for device-visible DVMA. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
`struct iounit_struct` persists the register pointer, IOPTE table, DVMA rotors, lock, and allocation bitmap while devices are active. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/spinlock.h>`, `<linux/pgtable.h>`, `<asm/page.h>`. Integration dependencies: `linux/spinlock.h`, `linux/pgtable.h`, `asm/page.h`, SBus DMA mapping, and page-table type definitions.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
bitmap range mistakes or stale IOPTEs can cause overlapping DMA mappings, data corruption, or device access to wrong physical pages.

### Test Signals
SPARC32 SBus DMA driver tests, DMA map/unmap stress, IOPTE dump validation, and lockdep-style coverage around bitmap allocation. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
