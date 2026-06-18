<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/floppy.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/floppy.h

## Purpose
`floppy.h` adapts the generic Linux floppy driver to m68k machines, mainly Q40 and Sun3x. It supplies controller discovery, IRQ registration, pseudo-DMA setup, DMA memory allocation, and the Q40 hard interrupt path expected by the shared floppy core.

## Important APIs, Types, and Functions
The header defines `FDC1`, `N_FDC`, `N_DRIVE`, `FLOPPY0_TYPE`, virtual-DMA wrappers such as `fd_request_dma()`, `fd_get_dma_residue()`, `fd_dma_setup()`, and `fd_dma_mem_alloc()`, and I/O helpers `fd_inb()`/`fd_outb()`. `m68k_floppy_init()` selects a Q40 ISA base or Sun3x setup. `floppy_hardint()` is the IRQ entry for Q40 programmed I/O transfers.

## Control Flow, State, and Persistence
State is static per translation unit: `virtual_dma_count`, `virtual_dma_residue`, `virtual_dma_addr`, `virtual_dma_mode`, and `doing_pdma`. Setup marks `use_virtual_dma` and `can_use_virtual_dma`, while interrupts copy bytes between `virtual_dma_addr` and the FDC data port until the status bits stop indicating DMA-ready.

## Dependencies and Integration Points
It depends on `<asm/io.h>`, `sun3xflop.h`, vmalloc/vfree, `dma_spin_lock`, and the generic floppy core symbols `floppy_interrupt`, `virtual_dma_port`, status/data register constants, and IRQ APIs. Q40 uses ISA `inb/outb`; Sun3x delegates I/O and IRQ setup to Sun3x helpers.

## Risks
Only Q40 and Sun3x are implemented; other m68k machines return no controller. Static inline state in a header is unusual but mirrors old floppy-driver include patterns. Pseudo-DMA depends on exact status-bit timing and can silently report residue if the FDC stops requesting data early. DMA memory uses `vmalloc`, so callers must not assume physical contiguity.

## Test Signals
Useful signals are Q40 and Sun3x boot/probe logs, floppy read/write interrupt completion, DMA residue accounting on short transfers, and regression builds for configurations without Q40/Sun3x support. There is no local unit-test surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/floppy.h -->
