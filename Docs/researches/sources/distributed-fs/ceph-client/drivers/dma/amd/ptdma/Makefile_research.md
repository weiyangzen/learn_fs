## sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/Makefile

### Purpose
This Makefile builds AMD PTDMA from core device, dmaengine, debugfs, and optional PCI glue objects.

### Important APIs, Types, And Functions
It builds `ptdma.o` when `CONFIG_AMD_PTDMA` is enabled from `ptdma-dev.o`, `ptdma-dmaengine.o`, and `ptdma-debugfs.o`, plus `ptdma-pci.o` when PCI is enabled.

### Control Flow, State, And Persistence
The composition mirrors the runtime split: PCI probe/resource setup, PT hardware queue management, dmaengine channel implementation, and debugfs reporting.

### Dependencies, Integration Points, Risks, And Test Signals
Risks include PCI-specific assumptions because PTDMA Kconfig already depends on PCI, and shared exports used by AE4DMA needing to be present when AE4DMA is enabled. Test signals include module link for PTDMA and AE4DMA users, debugfs object inclusion, and PCI object inclusion under expected configs.
