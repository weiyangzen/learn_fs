# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/gm20b.c

## Purpose
Implements Tegra GM20B ACR support, where WPR is preconfigured by firmware/registers and the driver allocates only the ucode blob.

## Important APIs, types, and functions
`gm20b_acr_wpr_alloc()` checks existing WPR bounds and allocates instance memory for the image. `gm20b_acr_hsfw_load_bld()` writes a v0 bootloader descriptor with shifted DMA bases. `gm20b_acr_load_setup()` fills `ucode_blob_base` and `ucode_blob_size`. `gm20b_acr_load()` loads only the load HS firmware.

## Control flow, state, and persistence
The function table reuses GM200 WPR parse/layout/build/patch/check and init. Load setup points the ACR firmware at the allocated ucode blob rather than programming WPR region properties.

## Dependencies and integration points
Depends on Tegra firmware declarations guarded by `CONFIG_ARCH_TEGRA_210_SOC`, PMU falcon HS firmware, and GM200 common WPR helpers.

## Risks and test signals
If the existing WPR is too small, init returns `-ENOSPC`. Signals include "WPR image too big" logs, ACR descriptor dump, and successful load firmware boot on Tegra.
