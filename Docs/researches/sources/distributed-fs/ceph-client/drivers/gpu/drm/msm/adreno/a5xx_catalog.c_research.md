# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a5xx_catalog.c

## Purpose
`a5xx_catalog.c` defines the static catalog for Adreno 5xx GPUs. It maps chip IDs to firmware, GMEM size, inactive period, quirks, ZAP shader firmware, GPMU firmware where present, and `a5xx_gpu_funcs`.

## Important APIs, Types, And Functions
The file defines `static const struct adreno_info a5xx_gpus[]` and exports it with `DECLARE_ADRENO_GPULIST(a5xx)`. Entries cover A505, A506, A508, A509, A510, A512, A530, and A540. Important metadata fields are `.fw`, `.gmem`, `.inactive_period`, `.quirks`, `.zapfw`, `.revn`, and `.funcs`.

## Control Flow
There is no direct control flow. Shared Adreno discovery matches chip IDs against this array and later runtime code branches on the selected info.

## State And Persistence
Catalog values persist in `adreno_gpu->info`. Quirks drive A5xx runtime workarounds such as two-pass WFI, fault-detect masking, and LMLOADKILL disable. Firmware names control PM4/PFP/GPMU buffer creation and secure ZAP loading.

## Dependencies And Integration Points
It includes `adreno_gpu.h` and `a5xx_gpu.h`. `a5xx_gpu.c` and `a5xx_power.c` consume this metadata for hardware init, GPMU setup, preemption decisions, and secure-mode exit.

## Risks
Wrong quirks or firmware names can produce subtle hangs or secure-world failures. Inactive periods are tuned for power-domain behavior on several parts. A509 intentionally reuses A512 ZAP firmware, and A530/A540 uniquely require GPMU firmware.

## Test Signals
Probe should request expected PM4/PFP/GPMU/ZAP files, select correct GMEM and speed behavior, and apply quirk-dependent register writes. Negative validation should check unsupported chip IDs do not match unintended entries.
