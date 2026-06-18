# sources/distributed-fs/ceph-client/arch/sparc/include/asm/leon.h

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
