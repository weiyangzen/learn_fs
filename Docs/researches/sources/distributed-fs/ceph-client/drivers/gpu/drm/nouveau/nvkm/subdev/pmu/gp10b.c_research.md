# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gp10b.c

## Purpose
Extends GM20B secure PMU support for GP10B, adding multi-falcon ACR bootstrap support and GP10B firmware declarations.

## Important APIs, Types, And Functions
`gp10b_pmu_acr_bootstrap_multiple_falcons()` sends `NV_PMU_ACR_CMD_BOOTSTRAP_MULTIPLE_FALCONS` and validates the returned mask. The `gp10b_pmu_acr` descriptor reuses GM20B loader write/patch and single-falcon bootstrap callbacks.

## Control Flow
Firmware version 0 loads signed PMU images through `gm20b_pmu_load()` and then uses GM20B PMU runtime handling. ACR may bootstrap PMU, FECS, and GPCCS either singly or by bitmask.

## State, Persistence, And Dependencies
State is the GM20B PMU state plus the ACR falcon mask and firmware images under `nvidia/gp10b/pmu/` on Tegra186 builds.

## Integration Points
Integrates with ACR LSF loading, nvfw PMU message formats, GM20B PMU runtime functions, and Tegra GP10B platform firmware packaging.

## Risks
The WPR low/high fields are left as placeholders in the command, so the firmware ABI must not require them here. Mask mismatch returns `-EIO` and can block dependent falcons.

## Test Signals
Signals include successful signed image load, bootstrap reply mask equality, FECS/GPCCS availability, and no PMU command queue timeouts.
