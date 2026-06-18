# sources/distributed-fs/ceph-client/arch/arc/include/asm/dma.h

Purpose: ARC legacy DMA address boundary definition. Important APIs/types/functions: defines `MAX_DMA_ADDRESS` as `0xC0000000`. Control flow: constant macro only. State and persistence: none. Dependencies/integration: used by memory-zone and DMA allocation code to distinguish directly DMA-addressable memory. Risks: platform memory maps that differ from this constant may misclassify DMA memory. Test signals: DMA allocation tests and platform boot with devices constrained below the boundary.
