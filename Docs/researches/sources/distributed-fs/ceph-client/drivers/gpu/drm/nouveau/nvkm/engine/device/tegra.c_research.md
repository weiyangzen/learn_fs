<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/tegra.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/tegra.c

Purpose: implements the platform-device transport constructor for Tegra integrated NVIDIA GPUs when `CONFIG_NOUVEAU_PLATFORM_DRIVER` is enabled. It adapts clocks, resets, regulator power, platform resources, IRQs, and optional IOMMU state to the generic `nvkm_device` interface.

Important APIs and functions: `nvkm_device_tegra_new()` is exported and returns `-ENOSYS` when the platform driver is disabled. Runtime helpers include `nvkm_device_tegra_power_up()`, `nvkm_device_tegra_power_down()`, `nvkm_device_tegra_probe_iommu()`, `nvkm_device_tegra_remove_iommu()`, BAR resource callbacks, and IRQ lookup. `nvkm_device_tegra_func` provides `.tegra`, `.dtor`, `.irq`, `.resource_addr`, `.resource_size`, and marks the device non-coherent.

Control flow: constructor allocates `struct nvkm_device_tegra`, maps resource 0, optionally acquires `vdd`, obtains reset and GPU/ref/pwr clocks, initializes the GPU clock if its rate is zero, sets the DMA mask from `func->iommu_bit`, probes an IOMMU domain, powers the GPU, stores Tegra speedo values, and calls `nvkm_device_ctor()` as `NVKM_DEVICE_TEGRA`. Error paths unwind power and IOMMU before freeing.

State and persistence: persistent state includes regulator/clock/reset handles, MMIO mapping, platform device pointer, speedo values, and optional IOMMU domain/MM allocator. Power state is externally visible through clocks/regulator/reset and may survive until destructor.

Dependencies and integration points: uses Linux platform, clk, reset, regulator, IOMMU, DMA mask, Tegra SKU/powergate APIs, and NVKM memory manager. It exposes only BAR0/PRI and BAR1/FB platform resources and the named `stall` IRQ.

Risks: power sequencing and reset/powergate ordering are timing-sensitive (`udelay` barriers). IOMMU setup depends on page-size compatibility and legacy ARM DMA-IOMMU detach behavior. Missing optional clocks/regulators or device-tree resource naming errors will fail probe.

Test signals: Tegra probe/remove, suspend/resume, IOMMU-enabled and disabled boot paths, DMA mapping above/below the configured bit width, and validation that BAR resources and `stall` IRQ match the device tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/tegra.c -->
