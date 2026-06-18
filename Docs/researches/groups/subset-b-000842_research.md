# subset-b-000842 Research

Grouped research for `subset-b-000842`. Each section preserves the source path in its title and is wrapped with deterministic markers for splitting into the mapped source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hypervisor.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/hypervisor.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/hypervisor.h` defines the sun4v/SPARC64 hypervisor ABI: trap numbers, error codes, service function ids, data-layout structs, and C prototypes for domain, CPU, MMU, interrupt, PCI, LDC, performance, and API-version hypercalls. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 3527 lines, 117692 bytes. Primary surface: `HV_FAST_TRAP`, `HV_CORE_TRAP`, `HV_E*` status codes, `sun4v_mach_*`, `sun4v_cpu_*`, `sun4v_mmu_*`, `sun4v_intr_*`, `sun4v_vintr_*`, PCI/IOMMU/MSI service ids, `sun4v_ldc_*`, `sun4v_*_perf*`, `sun4v_hvapi_*`, `struct hv_tsb_descr`, `struct hv_fault_status`, `struct ldc_mtable_entry`, `struct hv_mmu_statistics`, and NCS/CCB/trap-trace structs. Symbol scan highlights: `_SPARC64_HYPERVISOR_H`, `HV_FAST_TRAP`, `HV_MMU_MAP_ADDR_TRAP`, `HV_MMU_UNMAP_ADDR_TRAP`, `HV_TTRACE_ADDENTRY_TRAP`, `HV_CORE_TRAP`, `HV_EOK`, `HV_ENOCPU`, `HV_ENORADDR`, `HV_ENOINTR`, `HV_EBADPGSZ`, `HV_EBADTSB`, `HV_EINVAL`, `HV_EBADTRAP`, `HV_EBADALIGN`, `HV_EWOULDBLOCK`, `HV_ENOACCESS`, `HV_EIO`, `HV_ECPUERROR`, `HV_ENOTSUPPORTED`, `HV_ENOMAP`, `HV_ETOOMANY`, `HV_ECHANNEL`, `HV_EBUSY`, and 447 more.

### Control Flow
callers marshal up to five 64-bit arguments in outgoing registers and enter fast traps or hyper-fast traps; the hypervisor returns status in `%o0` and optional return values in the remaining registers. Higher-level SPARC64 code uses the declared wrappers to configure CPUs and mondo queues, install MMU/TSB state, manipulate interrupts, configure PCI IOMMU/MSI queues, exchange LDC data, and negotiate hypervisor API versions. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
the header stores no data itself, but its layouts describe persistent hypervisor-owned or guest-owned real-memory state such as machine descriptions, CPU queues, fault-status blocks, trap-trace buffers, PCI IOTSBs, LDC queues/map tables, and reboot/performance metadata. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: no direct include directives. Integration dependencies: `linux/bitops.h`-style bit macros through included kernel headers, assembler callers, SPARC64 trap assembly, sun4v kernel code, PCI, LDC, perf, NCS, and machine-description parsing.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
ABI drift is the main risk: trap ids, bit positions, struct offsets, register volatility, real-address alignment, and page-size encodings must match firmware. Hypercall wrappers must handle nonzero `HV_E*` statuses and partial delivery semantics such as mondo-send CPU-list updates.

### Test Signals
sun4v defconfig cross-build, boot on sun4v/LDOM capable systems, hypervisor API version negotiation tests, CPU hotplug/mondo/interrupt tests, PCI DMA/MSI validation, LDC link bring-up, and sparse/build coverage for assembler/C offset users. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hypervisor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/idprom.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/idprom.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/idprom.h` declares the SPARC IDPROM layout containing format, machine type, Ethernet address, manufacturing date, serial number, checksum, and reserved bytes. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 26 lines, 656 bytes. Primary surface: `struct idprom`, global `idprom`, and `idprom_init()`. Symbol scan highlights: `_SPARC_IDPROM_H`, `struct idprom`, `idprom_init`.

### Control Flow
early PROM/platform code reads firmware IDPROM contents into the structure, verifies or consumes the checksum, then exposes machine identity data to architecture setup and networking identity paths. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
the global pointer refers to boot-time firmware identity data that persists in kernel memory after initialization. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/types.h>`. Integration dependencies: `linux/types.h`, PROM accessors from `oplib.h`, and machine-type definitions.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong structure packing or checksum handling can misidentify machines or corrupt derived MAC address information.

### Test Signals
SPARC boot logs, IDPROM checksum validation, MAC address derivation checks, and compile coverage for both 32-bit and 64-bit SPARC. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/idprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/intr_queue.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/intr_queue.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/intr_queue.h` defines sun4v interrupt-queue head and tail register offsets for CPU mondo, device mondo, resumable error, and non-resumable error queues. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 16 lines, 794 bytes. Primary surface: `INTRQ_CPU_MONDO_HEAD/TAIL`, `INTRQ_DEVICE_MONDO_HEAD/TAIL`, `INTRQ_RESUM_MONDO_HEAD/TAIL`, and `INTRQ_NONRESUM_MONDO_HEAD/TAIL`. Symbol scan highlights: `_SPARC64_INTR_QUEUE_H`, `INTRQ_CPU_MONDO_HEAD`, `INTRQ_CPU_MONDO_TAIL`, `INTRQ_DEVICE_MONDO_HEAD`, `INTRQ_DEVICE_MONDO_TAIL`, `INTRQ_RESUM_MONDO_HEAD`, `INTRQ_RESUM_MONDO_TAIL`, `INTRQ_NONRESUM_MONDO_HEAD`, `INTRQ_NONRESUM_MONDO_TAIL`.

### Control Flow
low-level interrupt code uses these offsets to read or update queue producer/consumer pointers while handling hypervisor-delivered mondo and error events. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
state lives in per-CPU queue registers or queue memory configured through hypervisor CPU queue calls. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: no direct include directives. Integration dependencies: sun4v interrupt trap handling, hypervisor CPU queue configuration, and assembly register access paths.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
incorrect offsets break interrupt queue draining and can stall CPU, device, or error interrupt delivery.

### Test Signals
sun4v interrupt stress, CPU cross-call/mondo tests, error queue injection when available, and disassembly checks for register offsets. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/intr_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/io-unit.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/io-unit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/io.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/io.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/io.h` selects the 32-bit or 64-bit SPARC I/O implementation and adds generic big-endian raw read/write aliases before including generic I/O helpers. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 24 lines, 649 bytes. Primary surface: `readb_be/readw_be/readl_be`, `writeb_be/writew_be/writel_be`, and inclusion of `io_32.h` or `io_64.h`. Symbol scan highlights: `___ASM_SPARC_IO_H`, `readb_be`, `readw_be`, `readl_be`, `writeb_be`, `writel_be`, `writew_be`.

### Control Flow
preprocessor selection routes architecture builds to the proper implementation; generic kernel code then sees standard Linux I/O accessors. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
no runtime state; it is an include-time dispatch layer. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/io_64.h>`, `<asm/io_32.h>`, `<asm-generic/io.h>`. Integration dependencies: `__sparc__`, `__arch64__`, `asm-generic/io.h`, and the architecture-specific I/O headers.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
selection mistakes expose the wrong address-space model or accessor semantics to drivers.

### Test Signals
32-bit and 64-bit SPARC cross-builds and compile coverage of drivers using endian-specific accessors. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/io_32.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/io_32.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/io_32.h` implements SPARC32 MMIO, SBus I/O memory copy/fill helpers, port mapping declarations, and SBus capability hooks. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 153 lines, 3430 bytes. Primary surface: `ioremap`, `iounmap`, `_memset_io`, `_memcpy_fromio`, `_memcpy_toio`, `sbus_read*`, `sbus_write*`, `sbus_memcpy_*`, `ioport_map`, `pci_iounmap`, `sbus_can_dma_64bit`, `sbus_can_burst64`, and `sbus_set_sbus64`. Symbol scan highlights: `__SPARC_IO_H`, `IO_SPACE_LIMIT`, `memset_io`, `memcpy_fromio`, `memcpy_toio`, `iounmap`, `_memset_io`, `_memcpy_fromio`, `_memcpy_toio`, `sbus_readb`, `sbus_readw`, `sbus_readl`, `sbus_writeb`, `sbus_writew`, `sbus_writel`, `sbus_memset_io`, `sbus_memcpy_fromio`, `sbus_memcpy_toio`, `ioport_unmap`, `struct pci_dev`, `pci_iounmap`, `sbus_can_dma_64bit`, `sbus_can_burst64`, `struct device`, and 2 more.

### Control Flow
generic helpers call into byte/word/long SBus accessors; copy/fill loops advance volatile `__iomem` pointers one byte at a time; port and PCI unmap operations are implemented outside the header. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
no owned state; state is in mapped device registers, SBus configuration, and external mapping tables. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/kernel.h>`, `<linux/ioport.h>  /* struct resource */`, `<asm-generic/io.h>`. Integration dependencies: `linux/kernel.h`, `linux/ioport.h`, `asm-generic/io.h`, `asm/page.h`, SBus accessors, and PCI/device code.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
volatile access ordering, endian assumptions, and byte-loop copies can break device protocols if optimized incorrectly; incorrect `ioremap` declarations affect all drivers.

### Test Signals
SBus driver probe tests, MMIO accessor build tests, sparse `__iomem` checks, and DMA-capability validation on SPARC32 hardware/emulation. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/io_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/io_64.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/io_64.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/io_64.h` provides SPARC64 raw, ordered, and relaxed MMIO accessors, port I/O helpers, SBus accessors, I/O copy/fill functions, and minimal mapping helpers. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 474 lines, 11456 bytes. Primary surface: `__raw_read/write{b,w,l,q}`, `read/write{b,w,l,q}`, `in/out{b,w,l}`, `outs*`, `ins*`, `reads*`, `writes*`, `ioremap`, `ioremap_np`, `iounmap`, `ioport_map`, `pci_iounmap`, `sbus_*`, and `of_ioremap/of_iounmap`. Symbol scan highlights: `__SPARC64_IO_H`, `pci_iomap`, `__raw_readb`, `__volatile__`, `__raw_readw`, `__raw_readl`, `__raw_readq`, `__raw_writeb`, `__raw_writew`, `__raw_writel`, `__raw_writeq`, `readb`, `readb_relaxed`, `readw`, `readw_relaxed`, `readl`, `readl_relaxed`, `readq`, `readq_relaxed`, `writeb`, `writeb_relaxed`, `writew`, `writew_relaxed`, `writel`, and 70 more.

### Control Flow
inline assembly uses SPARC ASIs for little-endian MMIO and normal stores/loads for raw access; ordered helpers add `membar #Sync`; repeated I/O forwards to string I/O functions; `ioremap` mostly converts physical addresses through `__va` because SPARC64 has direct kernel mappings for these ranges. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
no owned state; it touches device registers, port windows, OF resource mappings, and kernel virtual-address layout globals such as `kern_base`, `kern_size`, and `PAGE_OFFSET`. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/kernel.h>`, `<linux/compiler.h>`, `<linux/types.h>`, `<asm/page.h>      /* IO address mapping routines need this */`, `<asm/asi.h>`, `<asm-generic/pci_iomap.h>`. Integration dependencies: `linux/kernel.h`, `linux/compiler.h`, `linux/types.h`, `asm/page.h`, `asm/asi.h`, `asm-generic/pci_iomap.h`, PCI, OF, and driver subsystems.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
missing barriers can reorder device transactions; ASI/endian misuse corrupts register access; direct-map assumptions in `ioremap` are architecture-sensitive.

### Test Signals
SPARC64 driver probe tests, endian MMIO tests, sparse `__iomem` checks, PCI/resource mapping tests, and disassembly checks for `membar` and ASI encodings. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/io_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ioctls.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/ioctls.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/ioctls.h` exports SPARC ioctl number definitions by including the UAPI header and generic termios ioctl helpers. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 14 lines, 358 bytes. Primary surface: `uapi/asm/ioctls.h` constants and `asm-generic/ioctls.h` fallback definitions. Symbol scan highlights: `_ASM_SPARC_IOCTLS_H`, `TIOCGETC`, `TIOCGETP`, `TIOCGLTC`, `TIOCSLTC`, `TIOCSETP`, `TIOCSETN`, `TIOCSETC`.

### Control Flow
userspace ABI constants are selected at include time; runtime behavior is implemented by tty and device ioctl handlers elsewhere. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
no state; it defines ABI numbers. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<uapi/asm/ioctls.h>`. Integration dependencies: SPARC UAPI headers and generic ioctl definitions.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
ABI drift would break existing SPARC user programs and tty tools.

### Test Signals
UAPI header install checks, strace/ioctl number compatibility, and SPARC userspace build tests. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ioctls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu-common.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu-common.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu-common.h` declares the common SPARC64 IOMMU allocation table used by PCI and ATU DMA mapping implementations. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 53 lines, 1445 bytes. Primary surface: `struct iommu_map_table`, `IOMMU_ERROR_CODE`, `IOMMU_POOL_HASHBITS`, and `iommu_tbl_pool_init()`. Symbol scan highlights: `_LINUX_IOMMU_COMMON_H`, `IOMMU_POOL_HASHBITS`, `IOMMU_NR_POOLS`, `IOMMU_ERROR_CODE`, `struct iommu_pool`, `struct iommu_map_table`, `IOMMU_HAS_LARGE_POOL`, `IOMMU_NO_SPAN_BOUND`, `IOMMU_NEED_FLUSH`, `iommu_tbl_pool_init`, `iommu_tbl_range_alloc`, `iommu_tbl_range_free`.

### Control Flow
IOMMU setup initializes pools over a DVMA range; DMA map/unmap code allocates table spans using the lock-protected map and per-pool hints. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
`struct iommu_map_table` persists allocation bitmaps, pool metadata, page shifts, DMA offset, and large-pool hints for a controller. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/spinlock_types.h>`, `<linux/device.h>`, `<asm/page.h>`. Integration dependencies: `linux/kernel.h`, `linux/bitmap.h`, `linux/spinlock.h`, `linux/mmzone.h`, and PCI/ATU IOMMU users.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong table sizing, page shift, or pool locking can lead to DVMA address reuse or leaks under concurrent DMA.

### Test Signals
PCI DMA mapping stress, IOMMU pool allocation/free tests, lockdep, and NUMA-node initialization coverage. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu.h` selects the 32-bit or 64-bit SPARC IOMMU header for the current build. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 9 lines, 215 bytes. Primary surface: include-time dispatch to `iommu_64.h` or `iommu_32.h`. Symbol scan highlights: `___ASM_SPARC_IOMMU_H`.

### Control Flow
preprocessor tests choose the proper register and data-structure model. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
no state; selected headers define state structures. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/iommu_64.h>`, `<asm/iommu_32.h>`. Integration dependencies: `__sparc__`, `__arch64__`, and the architecture-specific IOMMU headers.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong dispatch would compile an incompatible DMA/IOMMU model.

### Test Signals
SPARC32 and SPARC64 defconfig builds. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu_32.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu_32.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu_32.h` defines the sun4m SPARC32 SBus IOMMU register block, control/error bits, IOPTE format, and invalidation helpers. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 122 lines, 5865 bytes. Primary surface: `struct iommu_regs`, `IOMMU_CTRL_*`, `IOMMU_AFSR_*`, `IOMMU_SBCFG_*`, `IOMMU_MFSR_*`, `IOPTE_*`, `struct iommu_struct`, `iommu_invalidate()`, and `iommu_invalidate_page()`. Symbol scan highlights: `_SPARC_IOMMU_H`, `struct iommu_regs`, `IOMMU_CTRL_IMPL`, `IOMMU_CTRL_VERS`, `IOMMU_CTRL_RNGE`, `IOMMU_RNGE_16MB`, `IOMMU_RNGE_32MB`, `IOMMU_RNGE_64MB`, `IOMMU_RNGE_128MB`, `IOMMU_RNGE_256MB`, `IOMMU_RNGE_512MB`, `IOMMU_RNGE_1GB`, `IOMMU_RNGE_2GB`, `IOMMU_CTRL_ENAB`, `IOMMU_AFSR_ERR`, `IOMMU_AFSR_LE`, `IOMMU_AFSR_TO`, `IOMMU_AFSR_BE`, `IOMMU_AFSR_SIZE`, `IOMMU_AFSR_S`, `IOMMU_AFSR_RESV`, `IOMMU_AFSR_ME`, `IOMMU_AFSR_RD`, `IOMMU_AFSR_FAV`, and 28 more.

### Control Flow
SBus DMA code programs the IOMMU base/control registers, fills IOPTEs, then flushes the whole IOMMU TLB or a single page via write-only registers. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
`struct iommu_struct` keeps mapped registers, IOPTE table, managed DVMA range, and allocation bitmap. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/page.h>`, `<asm/bitext.h>`. Integration dependencies: `asm/page.h`, `asm/bitext.h`, `sbus_writel`, SBus DMA, and page-table types.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
register layout or bit mismatch causes DMA faults; incomplete invalidation can leave stale translations active.

### Test Signals
sun4m SBus DMA tests, IOMMU fault injection/logging, and map/unmap/invalidate stress. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu_64.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu_64.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu_64.h` defines SPARC64 IOMMU, streaming buffer, and ATU data structures and 64-bit IOPTE encoding. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 93 lines, 2489 bytes. Primary surface: `IOPTE_*`, `IOMMU_NUM_CTXS`, `struct iommu_arena`, `struct atu_iotsb`, `struct atu`, `struct iommu`, `struct strbuf`, and `iommu_table_init()`. Symbol scan highlights: `_SPARC64_IOMMU_H`, `IOPTE_VALID`, `IOPTE_64K`, `IOPTE_STBUF`, `IOPTE_INTRA`, `IOPTE_CONTEXT`, `IOPTE_PAGE`, `IOPTE_CACHE`, `IOPTE_WRITE`, `IOMMU_NUM_CTXS`, `struct iommu_arena`, `ATU_64_SPACE_SIZE`, `struct atu_iotsb`, `struct atu_ranges`, `struct atu`, `struct iommu_map_table`, `struct iommu`, `struct strbuf`, `iommu_table_init`.

### Control Flow
PCI controller setup initializes IOMMU map tables and optional ATU IOTSBs; DMA code allocates DVMA addresses, writes 64-bit IOPTEs, manages context bitmaps, and flushes IOMMU/streaming-buffer state. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
`struct iommu` persists page tables, register addresses, context bitmap, locks, dummy pages, and DMA mask; `struct strbuf` persists streaming-buffer registers and flush flag memory. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/iommu-common.h>`. Integration dependencies: `asm/iommu-common.h`, PCI controller code, hypervisor PCI services, spinlocks, DMA mapping, and NUMA allocation.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
context bitmap leaks, bad DMA mask handling, and streaming-buffer flush bugs can corrupt PCI DMA; ATU range assumptions affect large DMA windows.

### Test Signals
SPARC64 PCI DMA stress, IOMMU context exhaustion tests, streaming-buffer flush validation, ATU/IOTSB boot coverage, and sparse checks. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq.h` selects the SPARC32 or SPARC64 IRQ contract. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 9 lines, 207 bytes. Primary surface: include-time dispatch to `irq_64.h` or `irq_32.h`. Symbol scan highlights: `___ASM_SPARC_IRQ_H`.

### Control Flow
architecture preprocessor selection exposes the right IRQ count, builder, and controller hooks. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
no state in this wrapper. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/irq_64.h>`, `<asm/irq_32.h>`. Integration dependencies: `__sparc__`, `__arch64__`, and architecture IRQ headers.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong selection breaks interrupt numbering and controller integration.

### Test Signals
SPARC32/SPARC64 build coverage and irqchip probe tests. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq_32.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq_32.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq_32.h` declares SPARC32 IRQ constants and helpers for building Linux virtual IRQs from PROM/SBus interrupt descriptions. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 24 lines, 498 bytes. Primary surface: `NR_IRQS`, `irq_canonicalize`, `NO_IRQ`, `__irq_ino`, `sparc_floppy_irq`, and `sparc_build_irq()`. Symbol scan highlights: `_SPARC_IRQ_H`, `NR_IRQS`, `irq_canonicalize`, `sun4d_init_sbi_irq`, `NO_IRQ`.

### Control Flow
platform discovery converts real firmware/device interrupt data into kernel IRQ numbers used by drivers and interrupt handlers. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
external `sparc_floppy_irq` tracks the floppy controller IRQ; the IRQ subsystem owns the rest. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/interrupt.h>`. Integration dependencies: `linux/interrupt.h`, `linux/linkage.h`, `linux/threads.h`, PROM/SBus probing, and irq core.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
bad IRQ construction routes devices to wrong handlers or exceeds `NR_IRQS`.

### Test Signals
SPARC32 boot/probe logs, SBus device interrupt tests, and generic IRQ debugfs/proc inspection. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq_64.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq_64.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq_64.h` declares SPARC64 IRQ limits, IRQ bucket encoding, interrupt builder hooks, softirq stack handling, and hypervisor interrupt helpers. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 98 lines, 3075 bytes. Primary surface: `NR_IRQS`, `irq_bucket`, `irq_canonicalize`, `__irq_ino`, `irq_alloc`, `irq_free`, `sun4u_build_irq`, `sun4v_build_irq`, `sun4v_build_virq`, `sun4v_build_msi`, `handler_irq`, `do_softirq_own_stack`, and `get_irq_regs`. Symbol scan highlights: `_SPARC64_IRQ_H`, `IMAP_VALID`, `IMAP_TID_UPA`, `IMAP_TID_JBUS`, `IMAP_TID_SHIFT`, `IMAP_AID_SAFARI`, `IMAP_AID_SHIFT`, `IMAP_NID_SAFARI`, `IMAP_NID_SHIFT`, `IMAP_IGN`, `IMAP_INO`, `IMAP_INR`, `ICLR_IDLE`, `ICLR_TRANSMIT`, `ICLR_PENDING`, `NR_IRQS`, `irq_install_pre_handler`, `irq_canonicalize`, `build_irq`, `sun4v_build_irq`, `sun4v_build_virq`, `sun4v_build_msi`, `sun4v_destroy_msi`, `sun4u_build_msi`, and 10 more.

### Control Flow
platform and PCI code allocate IRQ buckets, map device/sysino/INO/MSI sources to Linux IRQs, and dispatch through low-level trap handlers while preserving register context. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
IRQ bucket arrays and per-CPU interrupt register state persist in IRQ core and low-level architecture code. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/linkage.h>`, `<linux/kernel.h>`, `<linux/errno.h>`, `<linux/interrupt.h>`, `<asm/pil.h>`, `<asm/ptrace.h>`. Integration dependencies: `linux/interrupt.h`, `linux/cache.h`, `linux/percpu.h`, `asm/pil.h`, hypervisor interrupt calls, PCI MSI, and irq core.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
bucket pointer/IRQ encoding errors, per-CPU register mishandling, or wrong mondo/sysino target programming can lose interrupts.

### Test Signals
SPARC64 boot with PCI/MSI devices, CPU hotplug interrupt retargeting, softirq stack tests, and interrupt storm handling. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/irqflags.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/irqflags.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/irqflags.h` selects SPARC32 or SPARC64 local IRQ flag primitives. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 9 lines, 227 bytes. Primary surface: include-time dispatch to `irqflags_64.h` or `irqflags_32.h`. Symbol scan highlights: `___ASM_SPARC_IRQFLAGS_H`.

### Control Flow
preprocessor selection exposes the correct privileged register operations. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
no wrapper state. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/irqflags_64.h>`, `<asm/irqflags_32.h>`. Integration dependencies: architecture-specific irqflag headers and generic interrupt code.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong primitives can leave interrupts enabled or disabled across critical sections.

### Test Signals
build coverage, lockdep/IRQ tracing, and interrupt enable/disable stress. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/irqflags_32.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/irqflags_32.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/irqflags_32.h` implements SPARC32 local interrupt enable/disable/save/restore helpers using `%psr` PIL bits and trap-enable state. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 48 lines, 1060 bytes. Primary surface: `arch_local_irq_save`, `arch_local_irq_restore`, `arch_local_irq_enable`, `arch_local_irq_disable`, `arch_local_save_flags`, `arch_irqs_disabled_flags`, `arch_irqs_disabled`, and `arch_safe_halt`. Symbol scan highlights: `_ASM_IRQFLAGS_H`, `arch_local_irq_restore`, `arch_local_irq_save`, `arch_local_irq_enable`, `arch_local_save_flags`, `volatile`, `arch_local_irq_disable`, `arch_irqs_disabled_flags`, `arch_irqs_disabled`.

### Control Flow
inline assembly reads `%psr`, manipulates `PSR_PIL`, writes the new value, and executes nops for pipeline synchronization; save/restore paths preserve caller interrupt state. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
state is the CPU processor status register interrupt level. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/types.h>`, `<asm/psr.h>`. Integration dependencies: `asm/psr.h`, privileged SPARC32 assembly, lock/interrupt core, and idle loop code.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
incorrect PSR synchronization or PIL masking can corrupt critical-section interrupt state.

### Test Signals
lockdep IRQ state checking, interrupt storm tests, idle/halt behavior, and disassembly review. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/irqflags_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/irqflags_64.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/irqflags_64.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/irqflags_64.h` implements SPARC64 local interrupt flag primitives using `%pstate` IE and PIL manipulation, with trace and raw variants. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 98 lines, 1954 bytes. Primary surface: `arch_local_irq_*`, `arch_irqs_disabled*`, `arch_safe_halt`, `raw_all_irq_*`, `raw_local_irq_*`, and low-level `__raw_local_irq_*` helpers. Symbol scan highlights: `_ASM_IRQFLAGS_H`, `arch_local_save_flags`, `__volatile__`, `arch_local_irq_restore`, `arch_local_irq_disable`, `arch_local_irq_enable`, `arch_irqs_disabled_flags`, `arch_irqs_disabled`, `arch_local_irq_save`.

### Control Flow
inline assembly reads/writes `%pstate` or `%pil`; generic IRQ tracing wraps the raw helpers when tracing is enabled. Safe halt enables interrupts before entering the idle trap path. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
state is held in CPU `%pstate` and `%pil` registers and reflected in tracing/accounting. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/pil.h>`. Integration dependencies: `linux/irqflags.h`, `asm/pstate.h`, `asm/pil.h`, SPARC64 trap code, and lockdep/irq tracing.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
PIL/IE ordering errors can unmask interrupts too early or leave CPUs non-preemptible; tracing wrappers must not recurse through raw paths.

### Test Signals
lockdep IRQ tracing, preemption/softirq stress, CPU idle tests, and low-level assembly inspection. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/irqflags_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/jump_label.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/jump_label.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/jump_label.h` defines SPARC jump-label/static-key patch records and branch encoding helpers for runtime code patching. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 52 lines, 1020 bytes. Primary surface: `JUMP_LABEL_NOP_SIZE`, `struct jump_entry`, `jump_entry_code/target/key`, `arch_static_branch`, `arch_static_branch_jump`, and `jump_label_apply_nops()`. Symbol scan highlights: `_ASM_SPARC_JUMP_LABEL_H`, `JUMP_LABEL_NOP_SIZE`, `arch_static_branch`, `goto`, `arch_static_branch_jump`, `struct jump_entry`.

### Control Flow
compiled static branches emit an annotated branch/nop sequence; runtime static-key updates patch branch destinations based on `jump_entry` metadata. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
jump table entries persist in special ELF sections and static-key state lives in generic jump-label code. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/types.h>`. Integration dependencies: `linux/types.h`, `linux/jump_label.h`, `asm/bug.h`, text patching, and compiler asm goto support.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
instruction encoding, alignment, or patch-size mistakes can corrupt executable text.

### Test Signals
jump-label selftests, static key toggling, objdump validation of emitted sequences, and SMP text-patching stress. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/jump_label.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/kdebug.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/kdebug.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/kdebug.h` selects SPARC32 or SPARC64 kernel-debug notifier definitions. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 9 lines, 219 bytes. Primary surface: include-time dispatch to `kdebug_64.h` or `kdebug_32.h`. Symbol scan highlights: `___ASM_SPARC_KDEBUG_H`.

### Control Flow
architecture selection exposes the right die-notifier enum and prototypes. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
no state in wrapper. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/kdebug_64.h>`, `<asm/kdebug_32.h>`. Integration dependencies: architecture-specific debug headers.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong selection breaks exception/debug notifier users.

### Test Signals
build coverage with kprobes, kgdb, and die notifier users. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/kdebug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/kdebug_32.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/kdebug_32.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/kdebug_32.h` declares SPARC32 die-notifier events and notifier-chain operations for traps, oopses, and debug exceptions. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 75 lines, 2043 bytes. Primary surface: `enum die_val`, `DIE_*` values, `notify_die`, `register_die_notifier`, and `unregister_die_notifier`. Symbol scan highlights: `_SPARC_KDEBUG_H`, `DEBUG_BP_TRAP`, `int`, `struct kernel_debug`, `sp_enter_debugger`, `__volatile__`, `SP_ENTER_DEBUGGER`, `enum die_val`, `KDEBUG_ENTRY_OFF`, `KDEBUG_DUNNO_OFF`, `KDEBUG_DUNNO2_OFF`, `KDEBUG_TEACH_OFF`.

### Control Flow
trap/oops/debug code calls `notify_die`; registered notifiers such as kprobes, kgdb, or tracing inspect `pt_regs` and can influence handling. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
notifier-chain state is maintained in architecture debug implementation files. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/openprom.h>`, `<asm/vaddrs.h>`. Integration dependencies: `linux/notifier.h`, `asm/ptrace.h`, trap/oops handling, kprobes, and kgdb.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
incorrect event numbers or notifier return handling can hide fatal traps or break probe recovery.

### Test Signals
kprobe hit/fault tests, kgdb trap tests, oops notifier coverage, and SPARC32 exception tests. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/kdebug_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/kdebug_64.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/kdebug_64.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/kdebug_64.h` declares SPARC64 die-notifier events and notifier registration for traps and debug faults. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 24 lines, 393 bytes. Primary surface: `enum die_val`, `notify_die`, `register_die_notifier`, and `unregister_die_notifier`. Symbol scan highlights: `_SPARC64_KDEBUG_H`, `struct pt_regs`, `bad_trap`, `enum die_val`.

### Control Flow
exception handlers emit typed die notifications with `pt_regs`; debugger/probe subsystems receive callbacks before default handling completes. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
notifier chain lives in SPARC64 debug implementation code. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: no direct include directives. Integration dependencies: `linux/notifier.h`, `asm/ptrace.h`, kprobes, kgdb, and trap handlers.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
notifier ordering or event mismatches can break kprobe single-step recovery and debugger stops.

### Test Signals
SPARC64 kprobes/kgdb tests, trap injection, and notifier registration build coverage. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/kdebug_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/kgdb.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/kgdb.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/kgdb.h` defines SPARC KGDB breakpoint encoding, register-packet sizing, and trap interface hooks. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 42 lines, 1014 bytes. Primary surface: `BREAK_INSTR_SIZE`, `arch_kgdb_ops`, `BUFMAX`, `NUMREGBYTES`, `kgdb_trap`, `kgdb_arch_set_pc`, and register enum values. Symbol scan highlights: `_SPARC_KGDB_H`, `BUFMAX`, `enum regnames`, `NUMREGBYTES`, `struct pt_regs`, `kgdb_trap`, `arch_kgdb_breakpoint`, `BREAK_INSTR_SIZE`, `CACHE_FLUSH_IS_SAFE`.

### Control Flow
KGDB plants a breakpoint instruction, trap code calls `kgdb_trap`, and the debugger serializes/deserializes SPARC register state according to the declared packet layout. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
debug session state is maintained by generic KGDB and trap handlers; this header defines architecture constants. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: no direct include directives. Integration dependencies: `asm/ptrace.h`, generic KGDB, trap handling, and register ABI definitions.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong register byte counts or PC update semantics make remote debugging unreliable.

### Test Signals
KGDB breakpoint, continue, single-step, and register read/write tests on SPARC configs. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/kgdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/kprobes.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/kprobes.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/kprobes.h` defines SPARC kprobe architecture support: breakpoint instruction, per-probe arch state, and single-step/emulation hooks. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 55 lines, 1312 bytes. Primary surface: `BREAKPOINT_INSTRUCTION`, `MAX_INSN_SIZE`, `struct arch_specific_insn`, `struct prev_kprobe`, `flush_insn_slot`, `kretprobe_blacklist_size`, and `arch_remove_kprobe()`. Symbol scan highlights: `_SPARC64_KPROBES_H`, `BREAKPOINT_INSTRUCTION`, `BREAKPOINT_INSTRUCTION_2`, `MAX_INSN_SIZE`, `kretprobe_blacklist_size`, `arch_remove_kprobe`, `flush_insn_slot`, `__kretprobe_trampoline`, `struct arch_specific_insn`, `struct prev_kprobe`, `struct kprobe`, `struct kprobe_ctlblk`, `kprobe_fault_handler`, `kprobe_trap`, `struct pt_regs`.

### Control Flow
kprobes copies and patches SPARC instructions into slots, installs breakpoint opcodes, handles trap callbacks, and may emulate or single-step original instructions. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
per-probe instruction copies and per-CPU previous-kprobe state persist while probes are armed. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm-generic/kprobes.h>`, `<linux/types.h>`, `<linux/percpu.h>`. Integration dependencies: `asm-generic/kprobes.h`, `asm/ptrace.h`, `asm/cacheflush.h`, text patching, and trap notifiers.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
SPARC delay slots, branch encodings, and cache flushing make probe placement risky; bad cleanup leaves patched text or stale instruction slots.

### Test Signals
kernel kprobes selftests, function-entry/return probe tests, branch-delay-slot rejection, and icache-flush validation. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/kprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ldc.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/ldc.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/ldc.h` declares the Logical Domain Channel API used by sun4v guest drivers for hypervisor-backed links, queues, shared-memory cookies, and domain variable/reboot/power operations. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 149 lines, 4474 bytes. Primary surface: `struct ldc_channel_config`, `LDC_MODE_*`, `LDC_EVENT_*`, `LDC_STATE_*`, `ldc_alloc/free/bind/unbind/connect/disconnect`, `ldc_read/write`, `ldc_map_sg`, `ldc_map_single`, `ldc_unmap`, `ldc_copy`, dring helpers, and `ldom_*` functions. Symbol scan highlights: `_SPARC64_LDC_H`, `ldom_set_var`, `ldom_reboot`, `ldom_power_off`, `struct ldc_channel_config`, `LDC_MODE_RAW`, `LDC_MODE_UNRELIABLE`, `LDC_MODE_RESERVED`, `LDC_MODE_STREAM`, `LDC_DEBUG_HS`, `LDC_DEBUG_STATE`, `LDC_DEBUG_RX`, `LDC_DEBUG_TX`, `LDC_DEBUG_DATA`, `LDC_EVENT_RESET`, `LDC_EVENT_UP`, `LDC_EVENT_DATA_READY`, `LDC_STATE_INVALID`, `LDC_STATE_INIT`, `LDC_STATE_BOUND`, `LDC_STATE_READY`, `LDC_STATE_CONNECTED`, `LDC_PACKET_SIZE`, `struct ldc_channel`, and 31 more.

### Control Flow
drivers allocate a channel, bind TX/RX queues with the hypervisor, optionally complete an LDC handshake, receive event callbacks for reset/up/data-ready, then send data or map/copy shared memory through transfer cookies. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
opaque `struct ldc_channel` owns queue, state-machine, mapping, and callback state; LDOM variable state is managed by hypervisor/domain services. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/hypervisor.h>`. Integration dependencies: `asm/hypervisor.h`, scatterlists, sun4v LDC hypercalls, vnet/vdisk/vio style drivers, and interrupt delivery.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
reset handling must fully reinitialize driver state; cookie permissions and map/unmap lifetimes are security-critical; queue state races can drop packets.

### Test Signals
LDOM virtual network/disk bring-up, LDC reset/reconnect stress, shared-ring copy/map tests, and event callback ordering tests. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ldc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/leon.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/leon.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/leon.h` defines LEON SPARC32 MMU/cache/IRQ constants, bypass register accessors, cache/TLB flush hooks, SMP hooks, and LEON page-table geometry. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 266 lines, 7848 bytes. Primary surface: `LEON_CNR_*`, `LEON_DIAGF_*`, `LEON_HARD_INT`, `leon_load_reg`, `leon_store_reg`, `LEON*_BYPASS_*`, cache/snooping helpers, `leon_switch_mm`, `leon_init_IRQ`, `leon_flush_*`, `leon_build_device_irq`, `leon_init_timers`, SMP boot/IPI helpers, and LEON page-table shift/mask macros. Symbol scan highlights: `LEON_H_INCLUDE`, `LEON_CNR_CTRL`, `LEON_CNR_CTXP`, `LEON_CNR_CTX`, `LEON_CNR_F`, `LEON_CNR_FADDR`, `LEON_CNR_CTX_NCTX`, `LEON_CNR_CTRL_TLBDIS`, `LEON_MMUTLB_ENT_MAX`, `LEON_DIAGF_LVL`, `LEON_DIAGF_WR`, `LEON_DIAGF_WR_SHIFT`, `LEON_DIAGF_HIT`, `LEON_DIAGF_HIT_SHIFT`, `LEON_DIAGF_CTX`, `LEON_DIAGF_CTX_SHIFT`, `LEON_DIAGF_VALID`, `LEON_DIAGF_VALID_SHIFT`, `LEON_HARD_INT`, `LEON_IRQMASK_R`, `LEON_IRQPRIO_R`, `LEON_MCFG2_SRAMDIS`, `LEON_MCFG2_SDRAMEN`, `LEON_MCFG2_SRAMBANKSZ`, and 68 more.

### Control Flow
LEON setup reads/writes ASI registers through bypass helpers, configures caches/snooping and timers, builds IRQs from AMBA/PROM data, and uses LEON-specific page-table geometry during MMU operations. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
hardware MMU/cache/IRQ registers persist device state; extern globals track flush policy, ticker IRQ, IPI IRQs, and trap entry points. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/irq.h>`, `<linux/interrupt.h>`. Integration dependencies: LEON ASIs, `linux/irq.h`, `linux/interrupt.h`, device tree nodes, SMP core, MMU/cache code, and `leon_amba.h`.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
inline ASI access is privileged and hardware-specific; page-size geometry must match configured kernel pages; cache snooping mistakes corrupt SMP memory.

### Test Signals
LEON3/LEON4 boot, SMP IPI and timer tests, cache/TLB flush stress, and cross-builds for each supported page-size option. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/leon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/leon_amba.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/leon_amba.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/leon_amba.h` describes LEON AMBA Plug and Play buses, UART/timer/IRQ register maps, vendor/device IDs, and exported AMBA discovery state. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 267 lines, 8283 bytes. Primary surface: `struct amba_prom_registers`, UART/PS2/timer/IRQ bit macros, `struct leon3_irqctrl_regs_map`, `struct leon3_apbuart_regs_map`, `struct leon3_gptimer_regs_map`, AMBA device tables, `_amba_init()`, AMBA globals, vendor/device id macros, and `amba_vendor/amba_device`. Symbol scan highlights: `LEON_AMBA_H_INCLUDE`, `struct amba_prom_registers`, `LEON_REG_UART_STATUS_DR`, `LEON_REG_UART_STATUS_TSE`, `LEON_REG_UART_STATUS_THE`, `LEON_REG_UART_STATUS_BR`, `LEON_REG_UART_STATUS_OE`, `LEON_REG_UART_STATUS_PE`, `LEON_REG_UART_STATUS_FE`, `LEON_REG_UART_STATUS_ERR`, `LEON_REG_UART_CTRL_RE`, `LEON_REG_UART_CTRL_TE`, `LEON_REG_UART_CTRL_RI`, `LEON_REG_UART_CTRL_TI`, `LEON_REG_UART_CTRL_PS`, `LEON_REG_UART_CTRL_PE`, `LEON_REG_UART_CTRL_FL`, `LEON_REG_UART_CTRL_LB`, `LEON3_GPTIMER_EN`, `LEON3_GPTIMER_RL`, `LEON3_GPTIMER_LD`, `LEON3_GPTIMER_IRQEN`, `LEON3_GPTIMER_SEPIRQ`, `LEON3_GPTIMER_TIMERS`, and 97 more.

### Control Flow
LEON platform discovery scans AMBA configuration areas, records AHB/APB devices, maps IRQ controller and timer registers, and makes discovered devices available to early console, timer, IRQ, and driver setup. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
global register pointers and AMBA device tables persist after discovery; timer and IRQ controller registers hold live hardware state. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: no direct include directives. Integration dependencies: device tree, LEON platform setup, APB/AHB device drivers, timer/IRQ code, and Gaisler vendor identifiers.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
incorrect device-id or config-area decoding causes missing devices or wrong register maps; fixed table sizes can overflow if scanning is not bounded.

### Test Signals
LEON AMBA probe logs, timer/IRQ/serial operation, device tree population checks, and bounds testing for bus scan tables. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/leon_amba.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/leon_pci.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/leon_pci.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/leon_pci.h` declares LEON PCI initialization entry points. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 23 lines, 512 bytes. Primary surface: `leon_pci_init()` and `leon_pci_grpci1_init()`. Symbol scan highlights: `_ASM_LEON_PCI_H_`, `struct leon_pci_info`, `struct pci_ops`, `struct resource`, `leon_pci_init`.

### Control Flow
platform setup calls these helpers to initialize generic LEON PCI support and GRPCI1 host controller support. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
PCI bus/controller state is allocated by implementation files and PCI core. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: no direct include directives. Integration dependencies: LEON platform setup, PCI core, and GRPCI host controller code.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
missing initialization leaves PCI devices undiscovered; host-controller variants must match hardware.

### Test Signals
LEON PCI boot/probe tests and PCI enumeration/resource assignment checks. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/leon_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/lsu.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/lsu.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/lsu.h` defines SPARC64 Load Store Unit control-register bits for cache, MMU, parity, and interrupt-control behavior. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 20 lines, 1062 bytes. Primary surface: `LSU_CONTROL_*` bit masks such as `LSU_CONTROL_DC`, `LSU_CONTROL_IC`, `LSU_CONTROL_DM`, `LSU_CONTROL_IM`, parity, write-buffer, and P0 watchpoint flags. Symbol scan highlights: `_SPARC64_LSU_H`, `LSU_CONTROL_PM`, `LSU_CONTROL_VM`, `LSU_CONTROL_PR`, `LSU_CONTROL_PW`, `LSU_CONTROL_VR`, `LSU_CONTROL_VW`, `LSU_CONTROL_FM`, `LSU_CONTROL_DM`, `LSU_CONTROL_IM`, `LSU_CONTROL_DC`, `LSU_CONTROL_IC`.

### Control Flow
low-level CPU setup and trap/MMU code uses these bit definitions when reading or programming LSU control state. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
state lives in the CPU LSU control register. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/const.h>`. Integration dependencies: SPARC64 CPU initialization, cache/MMU enable paths, and assembly register access.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong bit definitions can disable caches/MMUs or alter parity/watchpoint behavior unexpectedly.

### Test Signals
SPARC64 boot, cache/MMU enable tests, and register bit disassembly/source review. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/lsu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/machines.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/machines.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/machines.h` defines SPARC machine type identifiers and helper macros for sun4, sun4c, sun4m, sun4d, sun4e, and LEON-style systems. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 51 lines, 1540 bytes. Primary surface: `enum sparc_cpu`, `sparc_cpu_model`, and `ARCH_SUN4*`/`ARCH_LEON` predicates. Symbol scan highlights: `_SPARC_MACHINES_H`, `struct Sun_Machine_Models`, `SM_ARCH_MASK`, `M_LEON`, `SM_SUN4M`, `SM_SUN4M_OBP`, `SM_TYP_MASK`, `M_LEON3_SOC`, `SM_4M_SS60`, `SM_4M_SS50`, `SM_4M_SS40`.

### Control Flow
early platform detection sets `sparc_cpu_model`; architecture and driver code branches on the helper macros for model-specific setup. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
`sparc_cpu_model` persists the detected machine class. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: no direct include directives. Integration dependencies: PROM/IDPROM probing, platform setup, and model-specific architecture code.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
misclassification selects wrong MMU, interrupt, or bus setup.

### Test Signals
boot logs across supported machine classes and unit-style checks of helper predicates. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/machines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mbus.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/mbus.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/mbus.h` defines MBUS module-id decoding, cache-controller constants, and helper macros for SPARC32 MBus-based systems. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 97 lines, 2996 bytes. Primary surface: `struct mbus_device`, `MBUS_*` manufacturer/module macros, `mbus_module_*` predicates, `mbus_read_*`, and cache-control bits. Symbol scan highlights: `_SPARC_MBUS_H`, `enum mbus_module`, `HWBUG_COPYBACK_BROKEN`, `HWBUG_ASIFLUSH_BROKEN`, `HWBUG_VACFLUSH_BITROT`, `HWBUG_KERN_ACCBROKEN`, `HWBUG_KERN_CBITBROKEN`, `HWBUG_MODIFIED_BITROT`, `HWBUG_PC_BADFAULT_ADDR`, `HWBUG_SUPERSCALAR_BAD`, `HWBUG_PACINIT_BITROT`, `MBUS_VIKING`, `MBUS_LSI`, `MBUS_ROSS`, `MBUS_FMI`, `ROSS_604_REV_CDE`, `ROSS_604_REV_F`, `ROSS_605`, `ROSS_605_REV_B`, `VIKING_REV_12`, `VIKING_REV_2`, `VIKING_REV_30`, `VIKING_REV_35`, `LSI_L64815`, and 6 more.

### Control Flow
CPU/bus discovery reads module IDs, decodes vendor and implementation, and selects cache/MMU workarounds or controller setup. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
module IDs and cache controller registers are hardware state; decoded values influence boot-time configuration. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/ross.h>    /* HyperSparc stuff */`, `<asm/viking.h>  /* Ugh, bug city... */`. Integration dependencies: SPARC32 CPU probing, MBus register access, cache/MXCC/Viking/TurboSparc handling, and platform setup.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong module decoding can skip necessary CPU/cache errata handling.

### Test Signals
SPARC32 boot on sun4m variants, module-id logs, cache controller tests, and cross-build coverage. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mbus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mc146818rtc.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/mc146818rtc.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/mc146818rtc.h` selects the SPARC32 or SPARC64 MC146818-compatible RTC access header. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 14 lines, 298 bytes. Primary surface: include-time dispatch to `mc146818rtc_64.h` or `mc146818rtc_32.h`. Symbol scan highlights: `___ASM_SPARC_MC146818RTC_H`.

### Control Flow
preprocessor selection exposes the proper RTC port/register access model. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
no state in wrapper. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/spinlock.h>`, `<asm/mc146818rtc_64.h>`, `<asm/mc146818rtc_32.h>`. Integration dependencies: architecture-specific RTC headers.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong dispatch breaks CMOS/RTC access.

### Test Signals
SPARC32/SPARC64 RTC read/write build and boot coverage. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mc146818rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mc146818rtc_32.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/mc146818rtc_32.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/mc146818rtc_32.h` declares SPARC32 RTC/Mostek register access helpers and RTC locking. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 30 lines, 699 bytes. Primary surface: `CMOS_READ`, `CMOS_WRITE`, `RTC_PORT`, `RTC_ALWAYS_BCD`, `mc146818_get_time`, `mc146818_set_time`, and RTC lock declarations. Symbol scan highlights: `__ASM_SPARC_MC146818RTC_H`, `RTC_PORT`, `RTC_ALWAYS_BCD`, `CMOS_READ`, `CMOS_WRITE`, `RTC_IRQ`.

### Control Flow
RTC code serializes access, selects the register, reads or writes the data path, and converts time through MC146818-compatible helpers. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
RTC hardware stores wall-clock values; locking state protects register access. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/io.h>`. Integration dependencies: generic MC146818 RTC code, Mostek/OBIO hardware, and timekeeping.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
bad BCD or register selection corrupts persistent RTC time.

### Test Signals
RTC read/write tests, boot time initialization, and concurrent access lock coverage. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mc146818rtc_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mc146818rtc_64.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/mc146818rtc_64.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/mc146818rtc_64.h` defines SPARC64 RTC access stubs/macros for systems where firmware/platform code owns RTC access details. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 29 lines, 689 bytes. Primary surface: `RTC_PORT`, `RTC_ALWAYS_BCD`, and CMOS access placeholders/macros used by generic RTC code. Symbol scan highlights: `__ASM_SPARC64_MC146818RTC_H`, `RTC_PORT`, `RTC_ALWAYS_BCD`, `CMOS_READ`, `CMOS_WRITE`.

### Control Flow
generic RTC paths compile against the architecture contract while implementation details are resolved by SPARC64 platform code. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
RTC state is in platform hardware/firmware, not this header. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/io.h>`. Integration dependencies: generic RTC/MC146818 code and SPARC64 platform time code.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
incomplete or incompatible macros cause generic RTC code to build but not access hardware correctly.

### Test Signals
SPARC64 timekeeping boot tests and RTC class driver coverage. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mc146818rtc_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mdesc.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/mdesc.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/mdesc.h` declares the sun4v machine-description parser API used to inspect hypervisor-provided topology, properties, arcs, and handles. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 99 lines, 3066 bytes. Primary surface: `struct mdesc_handle`, `mdesc_grab`, `mdesc_release`, node iteration helpers, `mdesc_get_property`, `mdesc_get_node`, `mdesc_node_by_name`, `mdesc_get_node_info`, `mdesc_for_each_node_by_name`, `mdesc_for_each_arc`, and notifier registration. Symbol scan highlights: `_SPARC64_MDESC_H`, `struct mdesc_handle`, `mdesc_release`, `MDESC_NODE_NULL`, `MDESC_MAX_STR_LEN`, `mdesc_node_by_name`, `mdesc_for_each_node_by_name`, `MDESC_ARC_TYPE_FWD`, `MDESC_ARC_TYPE_BACK`, `mdesc_next_arc`, `mdesc_for_each_arc`, `mdesc_arc_target`, `mdesc_update`, `struct mdesc_notifier_client`, `mdesc_register_notifier`, `struct vdev_port`, `struct ds_port`, `mdesc_get_node`, `mdesc_get_node_info`, `mdesc_fill_in_cpu_data`, `mdesc_populate_present_mask`, `mdesc_get_page_sizes`, `sun4v_mdesc_init`.

### Control Flow
sun4v code grabs a machine-description snapshot, walks nodes and arcs, extracts typed properties, then releases the handle; update notifiers let subsystems respond to hypervisor description changes. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
machine-description snapshots persist while referenced; notifier chains track registered consumers. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/types.h>`, `<linux/cpumask.h>`, `<asm/prom.h>`. Integration dependencies: `linux/types.h`, `linux/notifier.h`, hypervisor `mach_desc` service, CPU/PCI/LDC topology code, and device discovery.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
property length/type assumptions can misparse firmware data; stale handles after MD updates can leave topology inconsistent.

### Test Signals
sun4v boot topology parsing, MD update notifier tests, property fuzzing with malformed descriptions, and LDOM configuration changes. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mdesc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/memctrl.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/memctrl.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/memctrl.h` declares SPARC memory-controller initialization. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 10 lines, 311 bytes. Primary surface: `memctrl_init()`. Symbol scan highlights: `_SPARC_MEMCTRL_H`, `int`, `register_dimm_printer`, `unregister_dimm_printer`.

### Control Flow
platform setup calls the initializer during boot to configure or discover memory-controller behavior. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
implementation-owned memory-controller state persists outside the header. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: no direct include directives. Integration dependencies: SPARC platform boot and memory-controller driver code.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
missing initialization can hide memory errors or platform-specific memory layout details.

### Test Signals
boot coverage and memory-controller probe logs. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/memctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mman.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/mman.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/mman.h` defines SPARC-specific memory-mapping flags and maps generic mmap protection/key constants into UAPI-visible values. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 91 lines, 2407 bytes. Primary surface: `MAP_RENAME`, `MAP_NORESERVE`, `MAP_INHERIT`, `MAP_LOCKED`, `MAP_GROWSDOWN`, `MAP_DENYWRITE`, `MAP_EXECUTABLE`, `MAP_POPULATE`, `MAP_NONBLOCK`, `MAP_STACK`, `MAP_HUGETLB`, `MAP_SYNC`, `MAP_FIXED_NOREPLACE`, `MCL_*`, `PKEY_*`, and inclusion of generic mmap constants. Symbol scan highlights: `__SPARC_MMAN_H__`, `arch_mmap_check`, `sparc_mmap_check`, `ipi_set_tstate_mcde`, `struct mm_struct`, `struct pt_regs`, `arch_calc_vm_prot_bits`, `sparc_calc_vm_prot_bits`, `arch_validate_prot`, `sparc_validate_prot`, `arch_validate_flags`.

### Control Flow
syscall and userspace ABI code consumes these constants when validating `mmap`, `mprotect`, `mlockall`, and pkey arguments. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
no state; constants become part of the SPARC user/kernel ABI. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<uapi/asm/mman.h>`, `<asm/adi_64.h>`. Integration dependencies: `uapi/asm-generic/mman-common.h`, MM syscall code, and libc headers.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
changing values breaks userspace ABI or syscall compatibility.

### Test Signals
UAPI header checks, mmap/mlock/pkey syscall tests on SPARC, and libc compatibility builds. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu.h` selects SPARC32 or SPARC64 MMU context definitions. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 9 lines, 207 bytes. Primary surface: include-time dispatch to `mmu_64.h` or `mmu_32.h`. Symbol scan highlights: `___ASM_SPARC_MMU_H`.

### Control Flow
preprocessor selection exposes the matching `mm_context_t` representation. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
no wrapper state. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/mmu_64.h>`, `<asm/mmu_32.h>`. Integration dependencies: architecture-specific MMU headers.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong context type breaks task memory-management structures.

### Test Signals
SPARC32/SPARC64 MM builds. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_32.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_32.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_32.h` defines the SPARC32 `mm_context_t` type as an unsigned long context identifier. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 11 lines, 209 bytes. Primary surface: `mm_context_t`. Symbol scan highlights: `__MMU_H`.

### Control Flow
MM code stores and switches SRMMU context identifiers through this scalar type. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
per-mm context values persist in `mm_struct`. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: no direct include directives. Integration dependencies: SPARC32 SRMMU context allocation and generic MM.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
type-size changes affect task context storage and context comparison.

### Test Signals
context switch, fork/exec/exit, and TLB shootdown tests on SPARC32. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_64.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_64.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_64.h` defines SPARC64 MM context state, TSB configuration, hugepage TSB indices, context bit encoding, and ADI-related fields. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 129 lines, 3969 bytes. Primary surface: `struct tsb_config`, `struct tsb_config_regs`, `mm_context_t`, `MM_TSB_*`, `CTX_*` helpers, and ADI fields within the context structure. Symbol scan highlights: `__MMU_H`, `CTX_NR_BITS`, `TAG_CONTEXT_BITS`, `CTX_VERSION_SHIFT`, `CTX_VERSION_MASK`, `CTX_PGSZ_8KB`, `CTX_PGSZ_64KB`, `CTX_PGSZ_512KB`, `CTX_PGSZ_4MB`, `CTX_PGSZ_BITS`, `CTX_PGSZ0_NUC_SHIFT`, `CTX_PGSZ1_NUC_SHIFT`, `CTX_PGSZ0_SHIFT`, `CTX_PGSZ1_SHIFT`, `CTX_PGSZ_MASK`, `CTX_PGSZ_BASE`, `CTX_PGSZ_HUGE`, `CTX_PGSZ_KERN`, `CTX_CHEETAH_PLUS_NUC`, `CTX_CHEETAH_PLUS_CTX0`, `CTX_NR_MASK`, `CTX_HW_MASK`, `CTX_FIRST_VERSION`, `CTX_VALID`, and 18 more.

### Control Flow
MM setup allocates per-mm context ids and TSB descriptors; context-switch code programs TSB base registers and secondary context values; ADI state tracks memory coloring/protection metadata. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
each `mm_struct` persists context id/version, TSB blocks/descriptors, cpumask lock, and optional ADI metadata. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/const.h>`, `<asm/page.h>`, `<asm/hypervisor.h>`. Integration dependencies: `linux/spinlock.h`, `linux/mm_types.h`, `asm/page.h`, `asm/adi_64.h`, TSB/MMU assembly, and hugepage code.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
context wrap, TSB descriptor mismatch, or ADI state errors cause stale translations or memory-tag faults.

### Test Signals
fork/exec/context rollover tests, TSB grow/shrink, hugepage and THP tests, ADI tests, and SMP TLB shootdown stress. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_context.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_context.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_context.h` selects the SPARC32 or SPARC64 MMU context-switch implementation. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 9 lines, 239 bytes. Primary surface: include-time dispatch to `mmu_context_64.h` or `mmu_context_32.h`. Symbol scan highlights: `___ASM_SPARC_MMU_CONTEXT_H`.

### Control Flow
generic scheduler/MM code includes this wrapper and receives architecture-specific context switch helpers. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
no wrapper state. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/mmu_context_64.h>`, `<asm/mmu_context_32.h>`. Integration dependencies: architecture-specific MMU context headers.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong selection breaks scheduler address-space switching.

### Test Signals
SPARC32/SPARC64 scheduler/MM cross-builds and context switch stress. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_context_32.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_context_32.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_context_32.h` declares SPARC32 context allocation and simple MM activation helpers. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 34 lines, 1084 bytes. Primary surface: `init_new_context`, `destroy_context`, `switch_mm`, `activate_mm`, `deactivate_mm`, `enter_lazy_tlb`, `get_mmu_context`, and `init_new_context_version`. Symbol scan highlights: `__SPARC_MMU_CONTEXT_H`, `init_new_context`, `destroy_context`, `switch_mm`, `struct task_struct`, `activate_mm`.

### Control Flow
new address spaces receive an SRMMU context, context switches load the hardware context when needed, and destroyed address spaces release their context. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
per-mm scalar context ids and global context allocator state persist outside the header. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm-generic/mm_hooks.h>`, `<asm-generic/mmu_context.h>`. Integration dependencies: SPARC32 SRMMU, generic scheduler/MM hooks, and TLB flush code.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
context reuse without proper TLB flushing can expose stale mappings across processes.

### Test Signals
fork/exec/exit stress, context rollover tests, TLB shootdown tests, and lazy TLB coverage. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_context_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_context_64.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_context_64.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_context_64.h` implements SPARC64 context-switch glue for TSB switching, secondary context loading, TLB flushing, and ADI MCDPER save/restore. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 198 lines, 5621 bytes. Primary surface: `get_new_mmu_context`, `init_new_context`, `destroy_context`, `__tsb_context_switch`, `tsb_context_switch_ctx`, `switch_mm`, `activate_mm`, `arch_start_context_switch`, `finish_arch_post_lock_switch`, and `mm_untag_mask`. Symbol scan highlights: `__SPARC64_MMU_CONTEXT_H`, `get_new_mmu_context`, `init_new_context`, `destroy_context`, `__tsb_context_switch`, `struct tsb_config`, `tsb_context_switch_ctx`, `tsb_context_switch`, `tsb_grow`, `smp_tsb_sync`, `load_secondary_context`, `__volatile__`, `__flush_tlb_mm`, `switch_mm`, `activate_mm`, `__HAVE_ARCH_START_CONTEXT_SWITCH`, `arch_start_context_switch`, `finish_arch_post_lock_switch`, `struct pt_regs`, `mm_untag_mask`.

### Control Flow
`switch_mm` records the active mm per CPU, allocates a context if invalid, unconditionally switches TSB state to avoid stale TSB growth races, flushes local TLBs for first-use contexts, and restores ADI/MCDPER state around scheduler switches. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
global context bitmaps/cache, per-CPU secondary-mm pointers, per-mm locks/TSB descriptors, and task flags for ADI state are live kernel state. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/spinlock.h>`, `<linux/mm_types.h>`, `<linux/smp.h>`, `<linux/sched.h>`, `<asm/spitfire.h>`, `<asm/adi_64.h>`, `<asm-generic/mm_hooks.h>`, `<asm/percpu.h>`, `<asm-generic/mmu_context.h>`. Integration dependencies: `linux/sched.h`, `linux/smp.h`, `asm/spitfire.h`, `asm/adi_64.h`, percpu support, generic MM hooks, and TLB flush implementation.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
the documented TSB grow race is high-risk; skipping a context switch or TLB flush can leave CPUs using stale TSBs. ADI register save/restore must match task flags and register encodings.

### Test Signals
SMP context-switch stress, TSB grow under CPU migration, THP/hugetlb workloads, ADI tests, and TLB shootdown validation. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_context_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmzone.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmzone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mxcc.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/mxcc.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/mxcc.h` defines MXCC external cache register addresses, bit masks, and inline ASI accessors for SPARC32 MBus systems. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 138 lines, 4431 bytes. Primary surface: `MXCC_*` register constants, stream/source/destination/cache-control bits, and inline helpers to read/write MXCC registers through ASI operations. Symbol scan highlights: `_SPARC_MXCC_H`, `MXCC_DATSTREAM`, `MXCC_SRCSTREAM`, `MXCC_DESSTREAM`, `MXCC_RMCOUNT`, `MXCC_STEST`, `MXCC_CREG`, `MXCC_SREG`, `MXCC_RREG`, `MXCC_EREG`, `MXCC_PREG`, `MXCC_STREAM_SIZE`, `MXCC_CTL_RRC`, `MXCC_CTL_PRE`, `MXCC_CTL_MCE`, `MXCC_CTL_PARE`, `MXCC_CTL_ECE`, `MXCC_ERR_ME`, `MXCC_ERR_CE`, `MXCC_ERR_PEW`, `MXCC_ERR_PEE`, `MXCC_ERR_ASE`, `MXCC_ERR_EIV`, `MXCC_ERR_MOPC`, and 8 more.

### Control Flow
cache-controller code uses the helpers to configure streaming cache, flush or invalidate MXCC state, and inspect error/status registers. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
MXCC hardware registers hold cache control, stream, error, and diagnostic state. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: no direct include directives. Integration dependencies: SPARC32 MBus/cache setup, ASI access, Viking/MXCC platform code, and memory/cache flush routines.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
incorrect register access can corrupt external-cache state or lose cache coherency.

### Test Signals
sun4m MXCC boot, cache flush stress, DMA coherency tests, and error-register diagnostics. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/mxcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/nmi.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/nmi.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/nmi.h` declares SPARC NMI support hooks for perf and watchdog-style interrupt handling. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 14 lines, 318 bytes. Primary surface: `arch_trigger_cpumask_backtrace`, `nmi_cpu_busy`, and related NMI declarations depending on config. Symbol scan highlights: `__NMI_H`, `nmi_init`, `perfctr_irq`, `nmi_adjust_hz`, `start_nmi_watchdog`, `stop_nmi_watchdog`.

### Control Flow
debug/watchdog/perf code calls architecture NMI hooks to interrupt CPUs or collect backtraces. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
NMI state is owned by perf/watchdog and interrupt code. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: no direct include directives. Integration dependencies: generic NMI/watchdog APIs, perf events, and SPARC interrupt handling.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
bad NMI routing can deadlock diagnostics or fail to capture hung CPUs.

### Test Signals
lockup detector, perf NMI sampling, and CPU backtrace trigger tests. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/nmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ns87303.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/ns87303.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/ns87303.h` defines National Semiconductor NS87303 Super I/O configuration registers, logical device selectors, and helper prototypes. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 118 lines, 3299 bytes. Primary surface: `FER`, `FAR`, `PTR`, `PCR`, `PMC`, logical device bits, power/IRQ/ECP masks, and `ns87303_modify()`/initialization helpers. Symbol scan highlights: `_SPARC_NS87303_H`, `FER`, `FAR`, `PTR`, `FCR`, `PCR`, `KRR`, `PMC`, `TUP`, `SID`, `ASC`, `CS0CF0`, `CS0CF1`, `CS1CF0`, `CS1CF1`, `FER_EDM`, `FAR_LPT_MASK`, `FAR_LPTB`, `FAR_LPTA`, `FAR_LPTC`, `PTR_LPTB_IRQ7`, `PTR_LEVEL_IRQ`, `PTR_LPT_REG_DIR`, `FCR_LDE`, and 25 more.

### Control Flow
platform or parport code selects Super I/O configuration registers and modifies masked bits to enable devices such as ECP parallel ports with correct IRQ polarity and modes. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
state lives in NS87303 configuration registers and any platform lock around config access. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/spinlock.h>`, `<asm/io.h>`. Integration dependencies: Ebus/parport support, ISA-like Super I/O accessors, `parport_64.h`, and platform probing.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong masks can disable serial/parallel/floppy functions or program incorrect IRQ behavior.

### Test Signals
ECPP parport probe, Super I/O register dump comparison, IRQ polarity tests, and regression boot on affected SPARC64 systems. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ns87303.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/obio.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/obio.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/obio.h` defines on-board I/O register addresses and inline helpers for BW/CC interrupt, profiling, and cache-controller registers on legacy SPARC systems. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 226 lines, 6412 bytes. Primary surface: `BW_*`, `CC_*`, `bw_get_intr_mask`, `bw_clear_intr_mask`, `bw_get/set_prof_limit`, `bw_get/set_ctrl`, `cc_get/set_*`, and related OBIO constants. Symbol scan highlights: `_SPARC_OBIO_H`, `CSR_BASE_ADDR`, `CSR_CPU_SHIFT`, `CSR_XDBUS_SHIFT`, `CSR_BASE`, `ECSR_BASE_ADDR`, `ECSR_CPU_SHIFT`, `ECSR_DEV_SHIFT`, `ECSR_BASE`, `ECSR_DEV_BASE`, `BW_LOCAL_BASE`, `BW_CID`, `BW_DBUS_CTRL`, `BW_DBUS_DATA`, `BW_CTRL`, `BW_INTR_TABLE`, `BW_INTR_TABLE_CLEAR`, `BW_PRESCALER`, `BW_PTIMER_LIMIT`, `BW_PTIMER_COUNTER2`, `BW_PTIMER_NDLIMIT`, `BW_PTIMER_CTRL`, `BW_PTIMER_COUNTER`, `BW_TIMER_LIMIT`, and 45 more.

### Control Flow
low-level interrupt/profile/cache code reads and writes memory-mapped OBIO registers using volatile accesses to mask interrupts, clear pending bits, and program counters. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
state persists in OBIO hardware interrupt masks, pending bits, profiling registers, and cache control registers. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/asi.h>`. Integration dependencies: legacy SPARC OBIO platform code, interrupt controllers, profiling timer, and cache-controller support.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
incorrect register offsets or masks can lose interrupts or disturb profiling/cache control.

### Test Signals
sun4c/sun4m OBIO boot tests, interrupt mask/pending tests, profiler timer checks, and hardware register diagnostics. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/obio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/opcodes.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/opcodes.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/opcodes.h` defines raw SPARC instruction encodings for crypto, CRC, and floating/integer register move opcodes used by inline assembly or generated code. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 100 lines, 2884 bytes. Primary surface: `F3F`, register field macros, `CRC32C`, `MD5`, `SHA*`, `AES_*`, `DES_*`, `CAMELLIA_*`, and `MOV*` opcode constants. Symbol scan highlights: `_SPARC_ASM_OPCODES_H`, `SPARC_CR_OPCODE_PRIORITY`, `F3F`, `FPD_ENCODE`, `RS1`, `RS2`, `RS3`, `RD`, `IMM5_0`, `IMM5_9`, `CRC32C`, `MD5`, `SHA1`, `SHA256`, `SHA512`, `AES_EROUND01`, `AES_EROUND23`, `AES_DROUND01`, `AES_DROUND23`, `AES_EROUND01_L`, `AES_EROUND23_L`, `AES_DROUND01_L`, `AES_DROUND23_L`, `AES_KEXPAND1`, and 24 more.

### Control Flow
assembly or C inline asm emits `.word` values from these macros when assembler mnemonics may not be available. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
no runtime state; constants become machine instructions. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: no direct include directives. Integration dependencies: SPARC crypto acceleration code, assembler, and CPU feature detection.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
one-bit encoding errors execute the wrong privileged/crypto instruction or trap on supported CPUs.

### Test Signals
objdump verification, crypto selftests on capable SPARC CPUs, and build tests with older assemblers. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/opcodes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/openprom.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/openprom.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/openprom.h` defines OpenBoot PROM vectors, device operations, memory lists, boot arguments, PROM node operations, and PROM property/register/range structures. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 280 lines, 7477 bytes. Primary surface: `LINUX_OPPROM_MAGIC`, `struct linux_romvec`, `linux_dev_v0_funcs`, `linux_dev_v2_funcs`, memory/boot-argument structs, `linux_nodeops`, `PROMREG_MAX`, `linux_prom_registers`, PCI range/register/intmap structs, and PROM device constants. Symbol scan highlights: `__SPARC_OPENPROM_H`, `LINUX_OPPROM_MAGIC`, `struct linux_dev_v0_funcs`, `struct linux_dev_v2_funcs`, `struct linux_mlist_v0`, `struct linux_mem_v0`, `struct linux_arguments_v0`, `struct linux_bootargs_v2`, `struct linux_romvec`, `struct linux_nodeops`, `PROMDEV_KBD`, `PROMDEV_SCREEN`, `PROMDEV_TTYA`, `PROMDEV_TTYB`, `int`, `PROMREG_MAX`, `PROMVADDR_MAX`, `PROMINTR_MAX`, `struct linux_prom_registers`, `struct linux_prom64_registers`, `struct linux_prom_irqs`, `struct linux_prom_ranges`, `struct linux_prom_pci_registers`, `struct linux_prom_pci_ranges`, and 2 more.

### Control Flow
early boot receives a PROM vector or client-interface handle, then PROM library code uses these structures to print, halt/reboot, traverse device trees, map devices, and collect memory/device properties. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
PROM vectors and memory lists are firmware-provided boot state; kernel copies or references selected values during early initialization. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/of.h>`. Integration dependencies: `linux/of.h`, `oplib_32.h`, `oplib_64.h`, platform boot code, device tree conversion, and bus probing.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
structure layout is firmware ABI; pointer-size and 32/64-bit range differences must remain exact or early boot/device discovery fails.

### Test Signals
PROM boot on sun4c/sun4m/sun4u/sun4v, device tree traversal tests, property/range parsing validation, and early console/halt paths. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/openprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib.h` selects the SPARC32 or SPARC64 OpenBoot PROM library interface. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 9 lines, 215 bytes. Primary surface: include-time dispatch to `oplib_64.h` or `oplib_32.h`. Symbol scan highlights: `___ASM_SPARC_OPLIB_H`.

### Control Flow
platform code includes a single header and receives the proper PROM API for its ABI. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
no wrapper state. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/oplib_64.h>`, `<asm/oplib_32.h>`. Integration dependencies: architecture-specific PROM library headers.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong dispatch breaks early boot and firmware calls.

### Test Signals
SPARC32/SPARC64 boot and PROM library build coverage. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib_32.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib_32.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib_32.h` declares the SPARC32 PROM library API for boot arguments, console, reboot/halt, IDPROM, memory lists, CPU start, device-tree traversal, range translation, and CPU discovery. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 184 lines, 6062 bytes. Primary surface: `romvec`, `prom_vers`, `prom_root_node`, `prom_nodeops`, `prom_init`, `prom_getbootargs`, `prom_reboot`, `prom_feval`, `prom_cmdline`, `prom_halt`, `prom_get_idprom`, `prom_*property`, `prom_finddevice`, `prom_apply_*ranges`, and CPU lookup helpers. Symbol scan highlights: `__SPARC_OPLIB_H`, `enum prom_major_version`, `prom_init`, `prom_reboot`, `prom_feval`, `prom_cmdline`, `prom_halt`, `void`, `prom_setsync`, `prom_get_idprom`, `prom_version`, `prom_getrev`, `prom_getprev`, `prom_console_write_buf`, `prom_write`, `prom_startcpu`, `prom_meminit`, `prom_getchild`, `prom_getsibling`, `prom_getproplen`, `prom_getproperty`, `prom_getint`, `prom_getintdefault`, `prom_getbool`, and 12 more.

### Control Flow
early setup initializes `romvec`, determines PROM version, uses PROM calls for console and device tree/property discovery, initializes physical memory, and starts secondary CPUs on supported systems. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
global PROM version, root node, nodeops pointer, and `prom_lock` persist after initialization. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/openprom.h>`, `<linux/spinlock.h>`, `<linux/compiler.h>`. Integration dependencies: `asm/openprom.h`, `linux/spinlock.h`, PROM firmware, platform boot, memory initialization, and device probing.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
PROM calls are early-boot and often non-reentrant; missing locking or wrong property buffer handling can break boot discovery.

### Test Signals
SPARC32 boot on PROM V0/V2/V3 machines, PROM property traversal, memory list validation, and console/reboot/halt tests. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib_64.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib_64.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib_64.h` declares the SPARC64/P1275 PROM client-interface API for boot, console, CPU control, power management, MMU mapping, memory retention, device-tree traversal, and direct CIF calls. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 253 lines, 8357 bytes. Primary surface: `prom_version`, `prom_root_node`, `prom_stdout`, `prom_chosen_node`, PROM method-name globals, `prom_init`, `prom_startcpu*`, `prom_sleepself/system`, `prom_retain`, `prom_itlb_load`, `prom_dtlb_load`, `PROM_MAP_*`, `prom_map/unmap`, property traversal, and `p1275_cmd_direct`. Symbol scan highlights: `__SPARC64_OPLIB_H`, `struct linux_mlist_p1275`, `struct linux_mem_p1275`, `prom_init`, `prom_init_report`, `prom_reboot`, `prom_feval`, `prom_cmdline`, `prom_halt`, `prom_halt_power_off`, `prom_get_idprom`, `prom_console_write_buf`, `prom_write`, `prom_startcpu`, `prom_startcpu_cpuid`, `prom_stopcpu_cpuid`, `prom_stopself`, `prom_idleself`, `prom_resumecpu`, `prom_sleepself`, `prom_sleepsystem`, `prom_wakeupsystem`, `prom_getunumber`, `prom_retain`, and 31 more.

### Control Flow
SPARC64 boot initializes the CIF handler, uses PROM services for early console and device tree access, may map/unmap client memory, starts/stops CPUs, and eventually minimizes PROM interaction after kernel services take over. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
PROM root/chosen/stdout handles and boot mapping globals persist as early-boot/platform state. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/openprom.h>`. Integration dependencies: `asm/openprom.h`, P1275 firmware, SPARC64 head/setup code, SMP boot, and OF/device-tree code.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
P1275 calls require exact argument cells and firmware-safe calling context; wrong map flags or TLB load parameters can corrupt early mappings.

### Test Signals
SPARC64/sun4v boot, early console, CPU bring-up, PROM property traversal, suspend/wakeup where supported, and map/unmap smoke tests. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/page.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/page.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/page.h` selects SPARC32 or SPARC64 page definitions. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 10 lines, 212 bytes. Primary surface: include-time dispatch to `page_64.h` or `page_32.h`. Symbol scan highlights: `___ASM_SPARC_PAGE_H`.

### Control Flow
generic MM includes this wrapper and receives matching page size, address conversion, and page-table scalar types. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
no wrapper state. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/page_64.h>`, `<asm/page_32.h>`. Integration dependencies: architecture-specific page headers.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong dispatch breaks all MM address conversions.

### Test Signals
SPARC32/SPARC64 MM builds and boot coverage. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/page_32.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/page_32.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/page_32.h` defines SPARC32 page helpers, physical-bank descriptors, page-table scalar types, task mmap base, and virtual/physical address conversion macros. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 136 lines, 3659 bytes. Primary surface: `clear_page`, `copy_page`, `clear_user_page`, `copy_user_page`, `struct sparc_phys_banks`, `sp_banks`, `pte_t/iopte_t/pmd_t/pgd_t/ctxd_t/pgprot_t`, `PAGE_OFFSET`, `phys_base`, `pfn_base`, `__pa`, `__va`, `virt_to_page`, and `virt_addr_valid`. Symbol scan highlights: `_SPARC_PAGE_H`, `clear_page`, `copy_page`, `clear_user_page`, `copy_user_page`, `struct sparc_phys_banks`, `SPARC_PHYS_BANKS`, `pte_val`, `iopte_val`, `pmd_val`, `pgd_val`, `ctxd_val`, `pgprot_val`, `iopgprot_val`, `__pte`, `__pmd`, `__iopte`, `__pgd`, `__ctxd`, `__pgprot`, `__iopgprot`, `TASK_UNMAPPED_BASE`, `PAGE_OFFSET`, `__pa`, and 6 more.

### Control Flow
MM and driver code uses page copy/clear helpers and address conversions; boot memory code fills `sp_banks`; user-page helpers flush D-cache aliases after writes. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
`sp_banks`, `phys_base`, and `pfn_base` persist boot memory layout; page table values persist in MM structures. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/const.h>`, `<vdso/page.h>`, `<asm-generic/memory_model.h>`, `<asm-generic/getorder.h>`. Integration dependencies: `linux/const.h`, `vdso/page.h`, cache flush code, generic memory model, and page allocator.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong base conversions corrupt DMA/page accounting; missing cache flushes can expose stale user mappings.

### Test Signals
memory init logs, page allocator tests, user copy/page-fault tests, and cache aliasing stress on SPARC32. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/page_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/page_64.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/page_64.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/page_64.h` defines SPARC64 page and hugepage sizes, page-table scalar types, cache alias indicators, user address-hole policy, and virtual/physical conversion helpers. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 161 lines, 4710 bytes. Primary surface: `HPAGE_*`, `REAL_HPAGE_*`, `HUGE_MAX_HSTATE`, `_clear_page`, `clear/copy_user_page`, `copy_highpage`, `pte_t/iopte_t/pmd_t/pud_t/pgd_t/pgprot_t`, `sparc64_va_hole_*`, `TASK_UNMAPPED_BASE`, `MAX_PHYS_ADDRESS_BITS`, `__pa`, `__va`, and `virt_addr_valid`. Symbol scan highlights: `_SPARC64_PAGE_H`, `DCACHE_ALIASING_POSSIBLE`, `HPAGE_SHIFT`, `REAL_HPAGE_SHIFT`, `HPAGE_16GB_SHIFT`, `HPAGE_2GB_SHIFT`, `HPAGE_256MB_SHIFT`, `HPAGE_64K_SHIFT`, `REAL_HPAGE_SIZE`, `HPAGE_SIZE`, `HPAGE_MASK`, `HUGETLB_PAGE_ORDER`, `HAVE_ARCH_HUGETLB_UNMAPPED_AREA`, `REAL_HPAGE_PER_HPAGE`, `HUGE_MAX_HSTATE`, `struct pt_regs`, `hugetlb_setup`, `WANT_PAGE_VIRTUAL`, `_clear_page`, `clear_page`, `struct page`, `clear_user_page`, `copy_page`, `copy_user_page`, and 31 more.

### Control Flow
MM code selects mmap bases around the VA hole, uses strict page-table wrapper types, handles hugepage sizing, and translates direct-map addresses through `PAGE_OFFSET`. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
`PAGE_OFFSET` and VA-hole globals persist for the booted layout; page table objects persist in MM structures. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/const.h>`, `<vdso/page.h>`, `<asm-generic/memory_model.h>`, `<asm-generic/getorder.h>`. Integration dependencies: `linux/const.h`, `vdso/page.h`, generic memory model, hugepage/THP code, and SPARC64 cache/TLB code.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
VA-hole bounds and hugepage shifts are ABI-sensitive; bad `__pa/__va` conversions break page allocator, DMA, and kernel direct map.

### Test Signals
SPARC64 boot, mmap layout tests for 32-bit and 64-bit tasks, hugetlb/THP tests, and virt/phys conversion sanity checks. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/page_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/parport.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/parport.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/parport.h` selects SPARC64-specific parallel-port support or the generic parport header. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 11 lines, 230 bytes. Primary surface: include-time dispatch to `parport_64.h` or `asm-generic/parport.h`. Symbol scan highlights: `___ASM_SPARC_PARPORT_H`.

### Control Flow
SPARC64 builds get EBus/ECPP handling, while other SPARC builds use generic parport behavior. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
no wrapper state. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/parport_64.h>`, `<asm-generic/parport.h>`. Integration dependencies: parport core and architecture-specific parport headers.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong dispatch can omit platform-specific DMA/IRQ setup for ECPP devices.

### Test Signals
parport_pc build/probe tests on SPARC64 and generic fallback builds. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/parport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/parport_64.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/parport_64.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/parport_64.h` implements SPARC64 parport_pc platform probing and EBus DMA shims for ECPP/parallel OpenFirmware devices. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 255 lines, 5863 bytes. Primary surface: `PARPORT_PC_MAX_PORTS`, DMA shim functions `request_dma/free_dma/enable_dma/disable_dma/set_dma_*`, `get_dma_residue`, `ecpp_probe`, `ecpp_remove`, `ecpp_match`, `ecpp_driver`, and `parport_pc_find_nonpci_ports`. Symbol scan highlights: `_ASM_SPARC64_PARPORT_H`, `PARPORT_PC_MAX_PORTS`, `HAS_DMA`, `DEFINE_SPINLOCK`, `claim_dma_lock`, `release_dma_lock`, `struct ebus_dma_info`, `struct parport`, `DECLARE_BITMAP`, `request_dma`, `free_dma`, `enable_dma`, `disable_dma`, `clear_dma_ff`, `set_dma_mode`, `set_dma_addr`, `set_dma_count`, `get_dma_residue`, `ebus_dma_residue`, `ecpp_probe`, `struct device_node`, `ecpp_remove`, `parport_pc_find_nonpci_ports`, `platform_driver_register`.

### Control Flow
platform driver probe maps OF resources, optionally registers an EBus DMA channel, configures NS87303 ECP/IRQ mode, calls `parport_pc_probe_port`, and unregisters/unmaps resources on remove. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
static `sparc_ebus_dmas` and `dma_slot_map` persist per parport; EBus DMA registers and parport core state are live while devices are bound. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/of.h>`, `<linux/platform_device.h>`, `<linux/string.h>`, `<asm/ebus_dma.h>`, `<asm/ns87303.h>`, `<asm/prom.h>`. Integration dependencies: `linux/of.h`, `linux/platform_device.h`, `asm/ebus_dma.h`, `asm/ns87303.h`, `asm/prom.h`, parport_pc, platform bus, and OF resources.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
slot allocation and cleanup must stay balanced; DMA lock shims are global; resource indexing assumes OF nodes provide expected register windows and IRQs.

### Test Signals
ECPP platform-device probe/remove, parport_pc transfer tests with FIFO/DMA enabled, OF resource failure injection, and lockdep around DMA lock usage. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/parport_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pbm.h -->
## sources/distributed-fs/ceph-client/arch/sparc/include/asm/pbm.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/pbm.h` defines SPARC PCI Bus Module software state compatible with SPARC64 PBM abstractions for SPARC PCIC/PCI code. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 48 lines, 1505 bytes. Primary surface: `struct linux_pbm_info` and `struct pcidev_cookie`. Symbol scan highlights: `__SPARC_PBM_H`, `struct linux_pbm_info`, `struct pci_bus`, `struct pcidev_cookie`, `struct device_node`.

### Control Flow
PCI probing creates a PBM record from PROM data, attaches the Linux PCI bus, and stores per-device cookies that point back to the PBM and PROM node. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
PBM and per-device cookies persist for PCI bus/device lifetime through PCI `sysdata` and driver data. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/pci.h>`, `<asm/oplib.h>`, `<asm/prom.h>`. Integration dependencies: `linux/pci.h`, `asm/oplib.h`, `asm/prom.h`, PCI core, PROM device tree, and SPARC PCIC code.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
bad PROM node association makes OBP-aware drivers use wrong firmware properties; bus numbering assumptions can break multi-bus probing.

### Test Signals
SPARC PCI enumeration, sysdata cookie inspection, OBP-aware PCI driver probe tests, and resource assignment validation. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/pbm.h -->
