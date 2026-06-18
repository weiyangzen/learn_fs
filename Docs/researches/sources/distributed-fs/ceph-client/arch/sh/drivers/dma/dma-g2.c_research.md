# sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dma-g2.c



Source read size: 197 lines, 4649 bytes.



Purpose: Sega Dreamcast G2 bus DMA provider for the legacy SH DMA API.

Important APIs/types/functions: packed/aligned `g2_channel`, `g2_status`, `g2_dma_info`, `g2_xfer_dma()`, `g2_dma_interrupt()`, `g2_get_residue()`, and `g2_dma_init()`.

Control flow: init requests the G2 DMA hardware event, writes wait-state/magic values, and registers four TEI-capable channels. Transfer validates 32-byte source/destination alignment, rounds size, maps destination into the G2 address window, flips direction semantics, flushes cache, programs the channel/status registers, and enables transfer. Interrupt checks completion status and wakes the channel waitqueue.

State and persistence: hardware DMA descriptor/status area at `0xa05f7800`, channel waitqueues, and registered DMA channel state persist while loaded.

Dependencies and integration points: depends on Dreamcast `sysasic` event IDs, `mach/dma.h`, SH cacheflush, and legacy DMA API.

Risks and test signals: undocumented control bits and magic values are hardware-sensitive; unaligned buffers are rejected; cache flush uses source/count assumptions. Test with G2 peripherals, aligned/unaligned transfers, IRQ completion, and residue polling.
