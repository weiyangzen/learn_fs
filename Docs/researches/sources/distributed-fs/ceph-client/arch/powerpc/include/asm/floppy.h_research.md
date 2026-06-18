## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/floppy.h

Purpose: supplies PowerPC-specific glue for the legacy PC floppy driver, including virtual DMA fallback.

Important APIs/types/functions: port I/O macros, DMA/IRQ macros, `struct fd_dma_ops`, static virtual DMA state, `floppy_hardint()`, virtual DMA helpers, `fd_request_irq()`, `vdma_dma_setup()`, `hard_dma_setup()`, real/virtual ops tables, `fd_request_dma()`, FDC base constants, drive counts, and floppy type defaults.

Control flow: request paths choose virtual DMA when `can_use_virtual_dma` allows it, otherwise request real ISA DMA. Hard DMA maps buffers through `isa_bridge_pcidev`, programs DMA registers, and caches the last mapping. Virtual DMA services bytes from the floppy data port in the interrupt handler until DMA/ready status changes, then calls the generic floppy interrupt.

State and persistence: static variables track virtual DMA count, residue, address, mode, active flag, selected ops, and cached real DMA mapping. Hardware FDC/DMA state persists across transfers.

Dependencies and integration: depends on generic floppy driver symbols, ISA DMA helpers, PCI `isa_bridge_pcidev`, DMA mapping API, IRQ API, and PowerPC machine-dependent I/O.

Risks and test signals: static cached DMA mapping can go stale if device lifetime changes; virtual DMA interrupt loops must not overrun buffers. Test signals include floppy probe/read/write on PowerPC systems with and without real DMA, DMA mapping error paths, IRQ handling, and module unload/free paths.
