## sources/distributed-fs/ceph-client/drivers/dma/amd/Kconfig

### Purpose
`drivers/dma/amd/Kconfig` defines selectable AMD DMA engine drivers for AE4DMA, PTDMA, and QDMA.

### Important APIs, Types, And Functions
Symbols are `AMD_AE4DMA`, `AMD_PTDMA`, and `AMD_QDMA`. AE4DMA depends on x86_64 or COMPILE_TEST plus PCI and also depends on PTDMA; PTDMA depends on x86_64 and PCI; QDMA depends on `HAS_IOMEM`. All select `DMA_ENGINE`, virtual-channel support, and QDMA additionally selects `REGMAP_MMIO`.

### Control Flow, State, And Persistence
These symbols control descent into `amd/ae4dma`, `amd/ptdma`, and `amd/qdma` Makefiles. AE4DMA reuses PTDMA's dmaengine layer, so the dependency on `AMD_PTDMA` is part of the functional build contract.

### Dependencies, Integration Points, Risks, And Test Signals
Risks include incorrect dependency visibility for COMPILE_TEST, hidden build assumptions between AE4DMA and PTDMA headers/exports, and QDMA register definitions being built without its core. Test signals include AMD submenu visibility, module and built-in combinations, AE4DMA with PTDMA enabled, QDMA allmodconfig coverage, and x86_64 PCI-only PTDMA selection.
