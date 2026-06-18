# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/nvjpg.c

Purpose: host1x/DRM client driver for Tegra210 NVJPG JPEG engine using Falcon firmware.

Important APIs/functions: `nvjpg_probe()` inherits DMA mask, maps registers, gets and maxes the NVJPG clock, initializes Falcon, and registers the host1x client. `nvjpg_init()/exit()` attach/detach IOMMU, register/unregister the Tegra DRM client, manage inherited DMA parameters, force runtime suspend, and free firmware memory. `nvjpg_load_falcon_firmware()` mirrors NVDEC Falcon loading with DMA API or shared Tegra DRM allocation depending on host1x client group. Runtime resume enables the clock, loads firmware once, and boots Falcon; suspend disables the clock. `nvjpg_can_use_memory_ctx()` explicitly reports memory contexts unsupported.

Control flow and state: `struct nvjpg` stores Falcon state, MMIO, DRM client, device, clock, and static config. Unlike NVDEC, no channel/open/submit callbacks are provided in this file, so it primarily registers engine capabilities and firmware boot state.

Dependencies/integration: depends on host1x client registration, Tegra DRM client lifecycle, runtime PM, Falcon helpers, DMA API, IOMMU attach, and firmware `nvidia/tegra210/nvjpg.bin`.

Risks: the exit path frees firmware memory based on fields populated only after runtime resume. If the device is registered but never resumed, zero/null handling must remain safe. Memory contexts are disabled, so callers must not assume group address-space support.

Test signals: probe/runtime resume, firmware missing/corrupt, autosuspend, IOMMU attach failure, and unload without prior firmware boot.
