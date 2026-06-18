# sources/distributed-fs/ceph-client/arch/mips/include/asm/jazzdma.h


### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/jazzdma.h` DMA mapping and legacy DMA programming contract, including address translation, controller registers, cache maintenance, or Jazz VDMA APIs. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 88 lines / 2826 bytes. macros/constants: `_ASM_JAZZDMA_H`, `VDMA_PAGESIZE`, `VDMA_PGTBL_ENTRIES`, `VDMA_PGTBL_SIZE`, `VDMA_PAGE_EMPTY`, `VDMA_PAGE`, `VDMA_OFFSET`, `JAZZ_R4030_CHNL_MODE`, `JAZZ_R4030_CHNL_ENABLE`, `JAZZ_R4030_CHNL_COUNT`, `JAZZ_R4030_CHNL_ADDR`, `R4030_CHNL_ENABLE`, `R4030_CHNL_WRITE`, `R4030_TC_INTR`, `R4030_MEM_INTR`, `R4030_ADDR_INTR`, `R4030_MODE_ATIME_40`, `R4030_MODE_ATIME_80`; types/functions/declarations: `extern unsigned long vdma_alloc(unsigned long paddr, unsigned long size);`, `extern int vdma_free(unsigned long laddr);`, `extern unsigned long vdma_phys2log(unsigned long paddr);`, `extern unsigned long vdma_log2phys(unsigned long laddr);`, `extern void vdma_stats(void);		/* for debugging only */`, `extern void vdma_enable(int channel);`, `extern void vdma_disable(int channel);`, `extern void vdma_set_mode(int channel, int mode);`, `extern void vdma_set_addr(int channel, long addr);`, `extern void vdma_set_count(int channel, int count);`, `extern int vdma_get_residue(int channel);`, `extern int vdma_get_enable(int channel);`, `typedef volatile struct VDMA_PGTBL_ENTRY {`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by block, network, floppy, SCSI, ISA/Jazz devices, and noncoherent cache paths. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong DMA address translation, cache flushing, locking, or channel programming can corrupt memory and page-cache data. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
