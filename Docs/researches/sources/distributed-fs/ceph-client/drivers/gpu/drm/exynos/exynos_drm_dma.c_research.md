# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_dma.c

Purpose: this file centralizes Exynos DRM DMA/IOMMU setup so display and processing subdevices share a consistent address space and DMA mapping device.

Important APIs: `exynos_drm_register_dma()` chooses the first registering subdevice as `priv->dma_dev`, creates or obtains `priv->mapping` when `CONFIG_EXYNOS_IOMMU` is active, and attaches each subdevice. `exynos_drm_unregister_dma()` detaches a subdevice. `exynos_drm_cleanup_dma()` releases the global mapping and clears the DMA device. Internal helpers `drm_iommu_attach_device()` and `drm_iommu_detach_device()` abstract ARM DMA-IOMMU and generic IOMMU-DMA paths.

Control flow: subdrivers call register during component bind and unregister during unbind. The first registration establishes the DMA mapping basis. For legacy `CONFIG_ARM_DMA_USE_IOMMU`, the code saves the original per-device DMA mapping in `*dma_priv`, detaches it, and attaches the shared Exynos mapping. On detach it restores the saved mapping. For `CONFIG_IOMMU_DMA`, it uses the domain associated with `priv->dma_dev` and calls `iommu_attach_device()` / `iommu_detach_device()`.

State and persistence: persistent runtime state is stored in `struct exynos_drm_private`: `dma_dev`, `mapping`, and each caller's `dma_priv`. The device virtual address window is fixed at `0x20000000` plus `0x40000000`.

Dependencies and integration points: this code depends on Linux DMA map ops, IOMMU APIs, optional ARM DMA-IOMMU APIs, and DRM private state from `exynos_drm_drv.h`. GEM allocation, framebuffer validation, G2D, FIMC, GSC, and FIMD all depend on the resulting DMA mapping.

Risks: attachment requires compatible DMA ops between the chosen DMA device and the subdevice; mismatches fail with `-EINVAL`. If a subdriver forgets unregister or passes the wrong `dma_priv`, legacy mapping restoration can be wrong. Non-IOMMU builds still set `dma_dev`, which affects GEM allocation through `to_dma_dev()`.

Test signals: probe all enabled subdrivers, deferred probe and module unload/reload, IOMMU and non-IOMMU kernels, PRIME import/export, and multi-device IPP jobs that DMA between GEM buffers.
