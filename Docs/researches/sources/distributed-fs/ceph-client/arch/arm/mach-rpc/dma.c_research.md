# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/dma.c

Purpose: RiscPC DMA implementation for IOMD channels, floppy FIQ DMA, and virtual sound DMA.

Important APIs/types/functions: defines `struct iomd_dma`, `iomd_get_next_sg()`, `iomd_dma_handle()`, `iomd_request_dma()`, `iomd_enable_dma()`, `iomd_disable_dma()`, `iomd_set_dma_speed()`, floppy FIQ operations, and `rpc_dma_init()`.

Control flow: init resets IOMD DMA control registers, sets timing/extension registers, attaches DMA ops to six IOMD channels, and registers virtual floppy/sound channels. Enabling an invalid channel maps ISA-style buffers if needed, initializes scatterlist state, clears the controller, then enables interrupts. The IRQ handler ping-pongs A/B DMA descriptors until end flags stop transfer. Floppy DMA claims FIQ and installs input/output assembly handlers.

State and persistence: per-channel `iomd_dma` holds current SG address/length and state. Hardware IOMD DMA registers and FIQ handler/registers are mutated.

Dependencies and integration points: integrates ISA DMA API, IOMD registers, ARM FIQ framework, `floppydma.S`, and legacy drivers expecting ISA-like DMA.

Risks: cache-coherence fallback mapping lacks visible unmap in this file. Descriptor boundary math is page/transfer-size sensitive. FIQ claim failure leaves floppy DMA inactive. Interrupt disable state must match hardware A/B state.

Test signals: ISA DMA channel registration, floppy read/write using FIQ, podule DMA, sound virtual DMA clients, residue reporting, and DMA speed register values.
