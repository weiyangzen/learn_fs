# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gm20b.c

## Purpose
Implements secure PMU firmware loading and ACR bootstrap support for GM20B Tegra GPUs.

## Important APIs, Types, And Functions
Important functions include `gm20b_pmu_load()`, `gm20b_pmu_init()`, `gm20b_pmu_recv()`, `gm20b_pmu_initmsg()`, `gm20b_pmu_acr_init_wpr()`, `gm20b_pmu_acr_bld_write()`, `gm20b_pmu_acr_bld_patch()`, and `gm20b_pmu_acr_bootstrap_falcon()`. `gm20b_pmu` is exported for GP10B reuse.

## Control Flow
Firmware is loaded as signed ACR LSF images. Init acquires the falcon, writes secure-mode args into DMEM, starts the falcon, waits for the first PMU init message, initializes HPQ/LPQ/message queues, sends WPR init, and receives later messages through the falcon message queue.

## State, Persistence, And Dependencies
State includes PMU command/message queues, `initmsg_received`, `wpr_ready` completion, WPR image contents, and falcon register/DMEM state. Firmware files under `nvidia/gm20b/pmu/` are module firmware dependencies.

## Integration Points
Integrates PMU, ACR, nvfw PMU/FLCN formats, core memory object access, and Tegra secure boot. FECS/GPCCS bootstrap callbacks rely on this PMU path.

## Risks
Secure boot is fragile: loader config address patching must preserve DMA-base encoding, queue indices are trusted from firmware, and WPR completion is asynchronous. Missing firmware falls back to a warning-only no-firmware mode.

## Test Signals
Signals are successful firmware request/load, init message parsing, WPR init completion, ACR bootstrap command replies matching requested falcon IDs, and no queue timeout logs.
