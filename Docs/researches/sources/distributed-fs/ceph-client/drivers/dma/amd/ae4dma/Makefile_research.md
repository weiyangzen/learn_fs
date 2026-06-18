## sources/distributed-fs/ceph-client/drivers/dma/amd/ae4dma/Makefile

### Purpose
This Makefile builds the AMD AE4DMA driver module/object from its device core and optional PCI bus glue.

### Important APIs, Types, And Functions
It creates `ae4dma.o` when `CONFIG_AMD_AE4DMA` is enabled, always includes `ae4dma-dev.o`, and adds `ae4dma-pci.o` when `CONFIG_PCI` is enabled.

### Control Flow, State, And Persistence
The build composition mirrors AE4DMA's runtime split: queue/work/IRQ core in `ae4dma-dev.c` and PCI discovery/resource setup in `ae4dma-pci.c`.

### Dependencies, Integration Points, Risks, And Test Signals
Risks include AE4DMA being selected without PCI support even though its Kconfig depends on PCI, and unresolved symbols if PTDMA exports are unavailable. Test signals include module link with `CONFIG_AMD_AE4DMA=m/y`, PCI enabled builds, and dependency on PTDMA object availability.
