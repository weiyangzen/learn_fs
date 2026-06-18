# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_dma.c

- Purpose: Implements the Mantis transport-stream DMA path using a coherent circular buffer and a small RISC program executed by the bridge.
- Important APIs/types/functions: `mantis_dma_init()`, `mantis_dma_exit()`, `mantis_dma_start()`, `mantis_dma_stop()`, `mantis_dma_xfer()`, internal buffer allocator, and RISC instruction macros.
- Control flow: Initialization allocates a 64 KiB coherent TS buffer and one page of coherent RISC code. Start builds WRITE commands for four 16 KiB blocks with 2 KiB transfers, points hardware at the RISC program, unmasks RISC interrupts, and enables FIFO/DCAP/RISC. IRQ updates `busy_block`; bottom-half work filters completed blocks into the DVB demux until `last_block` catches up. Stop disables hardware and masks DMA interrupts.
- State and persistence: State is held in `buf_cpu/buf_dma`, `risc_cpu/risc_dma`, `last_block`, and `busy_block`; no persistence. The ring position is reconstructed at stream start.
- Dependencies and integration points: Feeds `dvb_dmx_swfilter()` or `dvb_dmx_swfilter_204()` according to board TS size; uses DMA coherent allocation and Mantis MMIO registers from `mantis_reg.h`.
- Risks: The ring is small and can overrun if bottom-half work is delayed. RISC program size depends on constants fitting in one page. Work and IRQ state must be stopped before freeing coherent buffers. `busy_block` is shared with ISR without an explicit lock.
- Test signals: Validate with sustained DVB capture for 188-byte and 204-byte TS boards, stream start/stop loops, module unload under streaming, and debug logs showing monotonic block advancement without queue stalls.
