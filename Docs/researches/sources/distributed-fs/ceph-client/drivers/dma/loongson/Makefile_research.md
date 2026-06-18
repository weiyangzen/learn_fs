
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/loongson/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dma/loongson/Makefile

Purpose: ties Loongson DMA Kconfig symbols to their implementation objects.

Important APIs and control flow: `LOONGSON1_APB_DMA` builds `loongson1-apb-dma.o`, `LOONGSON2_APB_DMA` builds `loongson2-apb-dma.o`, and `LOONGSON2_APB_CMC_DMA` builds `loongson2-apb-cmc-dma.o`.

State and persistence behavior: no runtime state exists; the Makefile affects build inclusion only.

Dependencies and integration points: depends on the local Kconfig symbols and the parent DMA Makefile descending into the Loongson subdirectory.

Risks and test signals: risks are object-name or symbol drift. Test signals are successful built-in/module object generation for each selected option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/loongson/Makefile -->
