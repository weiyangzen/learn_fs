# sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dma-sh.c



Source read size: 425 lines, 9253 bytes.



Purpose: legacy SH on-chip DMAC provider implementing channel programming, transfer-end interrupts, residue calculation, DMAOR reset, and address-error handling.

Important APIs/types/functions: `sh_dmac_init()`, `sh_dmac_xfer_dma()`, `sh_dmac_configure_channel()`, `sh_dmac_get_dma_residue()`, `dma_tei()`, `dmaor_reset()`, `dmae_irq_init()`, register helpers `dma_base_addr()`/`dma_find_base()`, and `sh_dmac_ops`.

Control flow: init installs optional DMA error IRQs, resets one or two DMAOR blocks, and registers channels. Request installs per-channel TEI IRQs. Transfers configure defaults if needed, disable the channel, write SAR/DAR only when safe for the channel mode, program TCR based on transmit-size shift, then enable DE/IE. TEI IRQ clears TE/DE/IE and wakes waiters; error IRQ resets DMAOR and disables the error IRQ.

State and persistence: DMAC CHCR/SAR/DAR/TCR/DMAOR registers, IRQ registrations, channel flags, and waitqueues persist during runtime.

Dependencies and integration points: depends on CPU-specific `dma-register.h`, Dreamcast cascade quirks, SH interrupt numbering, legacy DMA API, and 29-bit/SoC-specific DMAC topology.

Risks and test signals: single-address mode can fault if SAR/DAR are written incorrectly; transmit-size shift table must match CHCR encoding; shared/multi IRQ mapping varies by CPU subtype. Test memory-to-memory and peripheral DMA modes, TEI wait, error IRQ recovery, Dreamcast PVR2 cascade, and dual-DMAC SoCs.
