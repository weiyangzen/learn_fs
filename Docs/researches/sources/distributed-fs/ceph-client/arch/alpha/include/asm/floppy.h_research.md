# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/floppy.h

This header provides Alpha-specific glue for the legacy floppy driver. It maps floppy I/O to ISA port access, wires floppy DMA and IRQ operations to Alpha DMA/IRQ helpers, and supplies a PCI DMA setup helper when `CONFIG_PCI` is enabled.

Important macros include `fd_inb/outb`, DMA request/free/enable/disable/mode/address/count helpers, IRQ request/free/enable/disable helpers, `fd_dma_setup`, `virtual_dma_init`, controller base constants `FDC1/FDC2`, and fixed floppy type constants. `alpha_fd_dma_setup` caches the last DMA mapping, unmaps it if address/size/direction changes, maps the new buffer through `isa_bridge->dev`, programs the 8237 DMA controller, sets `virtual_dma_port`, and enables DMA.

State includes static cached `bus_addr`, previous buffer metadata, controller globals, DMA controller registers, and `virtual_dma_port`. Risks include cached DMA mapping lifetime, direction mapping, ISA bridge availability, fixed CMOS-less drive type assumptions, and legacy DMA boundary rules inherited from `dma.h`. Tests are floppy build coverage and real/virtual floppy read/write where hardware exists.
