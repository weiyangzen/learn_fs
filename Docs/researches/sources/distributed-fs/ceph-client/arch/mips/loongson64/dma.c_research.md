<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/dma.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/dma.c

Purpose: Implements Loongson-3 DMA/physical address conversion and initializes SWIOTLB.

Important APIs/types/functions: `phys_to_dma()`, `dma_to_phys()`, and `plat_swiotlb_setup()`.

Control flow: Conversion extracts two node-id bits from physical bit 44-45 and embeds them at firmware/bridge-selected `node_id_offset` in the DMA address; reverse conversion extracts from DMA and restores physical node bits. SWIOTLB is initialized verbose and forced.

State and persistence: Depends on global `node_id_offset` set by early bridge config.

Dependencies and integration: Used by Linux direct DMA mapping; early config comes from `init.c` and firmware bridge detection in `env.c`.

Risks: Wrong `node_id_offset` breaks DMA on multi-node systems. The XOR/or expression assumes only two node bits are used.

Test signals: DMA mappings for buffers on different nodes should encode and decode node IDs correctly; SWIOTLB should initialize during boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/dma.c -->
