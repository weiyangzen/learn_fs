## sources/distributed-fs/ceph-client/drivers/dma/amd/Makefile

### Purpose
`drivers/dma/amd/Makefile` routes AMD DMA Kconfig symbols to their driver subdirectories.

### Important APIs, Types, And Functions
It descends into `ae4dma/`, `ptdma/`, and `qdma/` through `obj-$(CONFIG_AMD_AE4DMA)`, `obj-$(CONFIG_AMD_PTDMA)`, and `obj-$(CONFIG_AMD_QDMA)`.

### Control Flow, State, And Persistence
No runtime state exists. The file is pure build orchestration and relies on subdirectory Makefiles to compose final module objects.

### Dependencies, Integration Points, Risks, And Test Signals
The file must match `amd/Kconfig` symbol names and subdirectory names. Test signals include enabling each AMD symbol independently where dependencies allow and verifying expected module objects are emitted.
