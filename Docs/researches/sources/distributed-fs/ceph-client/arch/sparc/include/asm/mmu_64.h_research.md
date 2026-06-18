# sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_64.h

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
