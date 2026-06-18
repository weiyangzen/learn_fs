<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/dma.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/dma.c

Purpose: Implements simple Fuloong 2E physical/DMA address translation.

Important APIs/types/functions: `phys_to_dma()` ORs bit 31; `dma_to_phys()` clears bit 31.

Control flow: Translation is stateless and symmetric for the low 2 GiB window.

State and persistence: No stored state.

Dependencies and integration: Overrides architecture DMA direct translation hooks for devices on this board.

Risks: Addresses above the assumed window are truncated on reverse translation.

Test signals: PCI DMA mappings should produce bus addresses with the 0x80000000 bit set and should map back to the original low physical address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/dma.c -->
