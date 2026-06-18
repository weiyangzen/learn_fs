# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/gp10b.c

## Purpose
Implements Tegra GP10B ACR support as a variant of GM20B with GP10B firmware names.

## Important APIs, types, and functions
`gp10b_acr_new()` constructs the ACR subdev using `gp10b_acr_fwif`. The function table uses GM20B load firmware functions and GM200 WPR helpers, with Tegra guarded MODULE_FIRMWARE declarations.

## Control flow, state, and persistence
Runtime behavior follows GM20B: use existing WPR bounds, build GM200-style WPR structures, boot load HS firmware, and do not register unload firmware.

## Dependencies and integration points
Depends on `CONFIG_ARCH_TEGRA_186_SOC` firmware availability, GM20B load setup, and GM200 WPR helpers.

## Risks and test signals
Firmware is only declared for Tegra 186 builds. Signals include WPR-size checks, firmware load success, and ACR load boot on GP10B platforms.
