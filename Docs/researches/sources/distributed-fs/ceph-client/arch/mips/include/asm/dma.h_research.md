# sources/distributed-fs/ceph-client/arch/mips/include/asm/dma.h


### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/dma.h` DMA mapping and legacy DMA programming contract, including address translation, controller registers, cache maintenance, or Jazz VDMA APIs. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 310 lines / 10047 bytes. macros/constants: `_ASM_DMA_H`, `dma_outb`, `dma_outb`, `dma_inb`, `MAX_DMA_CHANNELS`, `MAX_DMA_ADDRESS`, `MAX_DMA_ADDRESS`, `MAX_DMA_PFN`, `MAX_DMA32_PFN`, `IO_DMA1_BASE`, `IO_DMA2_BASE`, `DMA1_CMD_REG`, `DMA1_STAT_REG`, `DMA1_REQ_REG`, `DMA1_MASK_REG`, `DMA1_MODE_REG`, `DMA1_CLEAR_FF_REG`, `DMA1_TEMP_REG`; types/functions/declarations: `extern spinlock_t  dma_spin_lock;`, `extern int request_dma(unsigned int dmanr, const char * device_id);	/* reserve a DMA channel */`, `extern void free_dma(unsigned int dmanr);	/* release it again */`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/io.h>			/* need byte IO */`, `<linux/spinlock.h>		/* And spinlocks */`, `<linux/delay.h>`.

### Integration Points
Used by block, network, floppy, SCSI, ISA/Jazz devices, and noncoherent cache paths. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Wrong DMA address translation, cache flushing, locking, or channel programming can corrupt memory and page-cache data. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
