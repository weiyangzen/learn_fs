# sources/distributed-fs/ceph-client/arch/sh/drivers/dma/Makefile



Source read size: 9 lines, 286 bytes.



Purpose: Kbuild selection for legacy SH DMA provider objects.

Important APIs/types/functions: builds `dma-sh.o`, `dma-api.o`, `dma-sysfs.o` for `SH_DMA_API`, plus optional `dma-pvr2.o`, `dma-g2.o`, and `dmabrg.o`.

Control flow: object inclusion follows Kconfig symbols for on-chip DMAC, Dreamcast peripherals, and SH7760 bridge DMA.

State and persistence: build graph only.

Dependencies and integration points: connects the legacy DMA API header contracts to controller implementations.

Risks and test signals: provider objects depend on CPU/board headers that may only exist for matching configs. Test enabled and disabled combinations.
