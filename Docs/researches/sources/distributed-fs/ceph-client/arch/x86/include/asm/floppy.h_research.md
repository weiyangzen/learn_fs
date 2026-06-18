<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/floppy.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/floppy.h

## Purpose
x86-specific floppy driver glue for ISA DMA, virtual DMA fallback, PIO interrupt handling, CMOS drive type reads, and controller constants. The header is 296 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/sizes.h>`; `#include <linux/vmalloc.h>`

Notable constants/macros: `#define _ASM_X86_FLOPPY_H`; `#define _CROSS_64KB(a, s, vdma) \`; `#define SW fd_routine[use_virtual_dma & 1]`; `#define CSW fd_routine[can_use_virtual_dma & 1]`; `#define fd_request_dma() CSW._request_dma(FLOPPY_DMA, "floppy")`; `#define fd_free_dma() CSW._free_dma(FLOPPY_DMA)`; `#define fd_enable_irq() enable_irq(FLOPPY_IRQ)`; `#define fd_disable_irq() disable_irq(FLOPPY_IRQ)`; `#define fd_free_irq() free_irq(FLOPPY_IRQ, NULL)`; `#define fd_get_dma_residue() SW._get_dma_residue(FLOPPY_DMA)`; `#define fd_dma_mem_alloc(size) SW._dma_mem_alloc(size)`; `#define fd_dma_setup(addr, size, mode, io) SW._dma_setup(addr, size, mode, io)`; `#define FLOPPY_CAN_FALLBACK_ON_NODMA`; `#define nodma_mem_alloc(size) vdma_mem_alloc(size)`; `#define fd_dma_mem_free(addr, size) _fd_dma_mem_free(addr, size)`; `#define fd_chose_dma_mode(addr, size) _fd_chose_dma_mode(addr, size)`; `#define FLOPPY0_TYPE \`; `#define FLOPPY1_TYPE \`

Notable declarations and inline helpers: `#define _ASM_X86_FLOPPY_H`; `#define _CROSS_64KB(a, s, vdma) \`; `#define SW fd_routine[use_virtual_dma & 1]`; `#define CSW fd_routine[can_use_virtual_dma & 1]`; `#define fd_request_dma() CSW._request_dma(FLOPPY_DMA, "floppy")`; `#define fd_free_dma() CSW._free_dma(FLOPPY_DMA)`; `#define fd_enable_irq() enable_irq(FLOPPY_IRQ)`; `#define fd_disable_irq() disable_irq(FLOPPY_IRQ)`; `#define fd_free_irq() free_irq(FLOPPY_IRQ, NULL)`; `#define fd_get_dma_residue() SW._get_dma_residue(FLOPPY_DMA)`; `#define fd_dma_mem_alloc(size) SW._dma_mem_alloc(size)`; `#define fd_dma_setup(addr, size, mode, io) SW._dma_setup(addr, size, mode, io)`; `#define FLOPPY_CAN_FALLBACK_ON_NODMA`; `static int virtual_dma_count;`; `static int virtual_dma_residue;`; `static char *virtual_dma_addr;`; `static int virtual_dma_mode;`; `static int doing_pdma;`; `static inline u8 fd_inb(u16 base, u16 reg)`; `u8 ret = inb_p(base + reg);`; `static inline void fd_outb(u8 value, u16 base, u16 reg)`; `static irqreturn_t floppy_hardint(int irq, void *dev_id)`; `unsigned char st;`; `static int calls;`

## Control Flow
The driver chooses hard DMA or virtual DMA, installs either floppy_interrupt or floppy_hardint, and the PIO interrupt loop drains/fills the FIFO until DMA status clears.

## State and Persistence
State is file-local static virtual_dma_* counters, current port/mode, doing_pdma, and FDC base addresses; CMOS reads are protected by rtc_lock.

## Dependencies and Integration Points
Integrates with legacy floppy core, ISA DMA APIs, IRQ request/free, port I/O helpers, vmalloc/free_pages, high_memory, and CMOS RTC access.

## Risks
Risks include residue accounting bugs, 64K boundary and 16MB ISA DMA constraints, IRQ handler races, stale virtual_dma_port assumptions, and very low hardware coverage.

## Test Signals
Tests need boot/module load on DMA and no-DMA paths, boundary-crossing buffers, vmalloc buffers, read/write interrupt residue behavior, and CMOS type detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/floppy.h -->
