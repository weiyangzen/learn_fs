# sources/distributed-fs/ceph-client/arch/sparc/include/asm/obio.h

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
