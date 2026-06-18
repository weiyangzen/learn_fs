## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dma-direct.h

Purpose: implements direct DMA address translation using per-device PowerPC DMA offsets.

Important APIs/types/functions: `phys_to_dma()` returns `paddr + dev->archdata.dma_offset`; `dma_to_phys()` returns `daddr - dev->archdata.dma_offset`.

Control flow: simple arithmetic conversion for direct-mapped DMA devices.

State and persistence: reads `dev->archdata.dma_offset`, which is set during device/bus setup and persists for the device lifetime.

Dependencies and integration: depends on `struct device` archdata from `device.h` and integrates with generic DMA-direct mapping.

Risks and test signals: a wrong offset causes devices to DMA to the wrong physical memory. Test signals include DMA API debug, device probe DMA masks, direct DMA transfers on offset and non-offset buses, and IOMMU-disabled boots.
