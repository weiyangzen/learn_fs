# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/dma.h

This header implements legacy ISA 8237 DMA controller definitions and helpers for Alpha PCs. It documents channel layout, byte/word transfer differences, boundary limits, count semantics, page-register mapping, and Alpha-specific high-page registers for 32-bit DMA addresses.

Important APIs and macros include `MAX_DMA_CHANNELS`, platform-specific `MAX_ISA_DMA_ADDRESS`, `MAX_DMA_ADDRESS`, controller register constants, `claim_dma_lock`, `release_dma_lock`, `enable_dma`, `disable_dma`, `clear_dma_ff`, `set_dma_mode`, `set_dma_ext_mode`, `set_dma_page`, `set_dma_addr`, `set_dma_count`, `get_dma_residue`, `request_dma`, `free_dma`, and `check_dma`. Helpers write port registers through `outb/inb` from `asm/io.h` and require interrupt-disabled serialized access around flip-flop-sensitive sequences.

State includes the external `dma_spin_lock`, DMA controller registers, page/high-page registers, and active channel reservations. Risks are old hardware constraints: 64K/128K boundary crossing, channel 5-7 word alignment, page register ordering, platform-specific address ceilings, and direct-map assumptions. Tests are floppy/ISA DMA users, DMA residue checks, and build coverage for platforms with and without PCI IOMMU support.
