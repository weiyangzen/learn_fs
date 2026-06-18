<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/dma.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/dma.c

Purpose: Implements Lemote 2F DMA address translation with a special high-address pass-through case.

Important APIs/types/functions: `phys_to_dma()` ORs 0x80000000. `dma_to_phys()` returns DMA addresses above 0x8fffffff unchanged, otherwise masks to low 28 bits.

Control flow: Translation is stateless; reverse mapping preserves some high bus addresses and strips the board DMA window for lower ones.

State and persistence: No stored state.

Dependencies and integration: Used by direct DMA mapping for Lemote 2F devices.

Risks: The threshold and 28-bit mask encode board-specific windows; devices outside these assumptions can map incorrectly.

Test signals: Network/storage DMA should work across low-memory buffers and any board-specific high DMA range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/dma.c -->
