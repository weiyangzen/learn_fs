# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a2xx_catalog.c

## Purpose
Registers catalog metadata for Adreno A2xx GPUs supported by the MSM DRM Adreno driver.

## Important APIs, types, and functions
- Static `a2xx_gpus[]` contains `struct adreno_info` entries for A200, i.MX51 A200 variant, A220, and A225.
- Each entry specifies chip IDs, family, revision number, firmware filenames, GMEM size, inactive period, and `a2xx_gpu_funcs`.
- `DECLARE_ADRENO_GPULIST(a2xx)` exports the catalog list to the Adreno device matching framework.

## Control flow
No executable control flow beyond static registration. At runtime, Adreno device matching scans declared GPU lists, matches chip IDs, loads the listed PM4/PFP firmware, and binds the A2xx function table.

## State and persistence
The catalog is static read-only driver data. Matched firmware names and GMEM sizes become part of runtime GPU device initialization state elsewhere.

## Dependencies and integration points
Depends on `adreno_gpu.h` for `struct adreno_info` and list declaration macros, and `a2xx_gpu.h` for `a2xx_gpu_funcs`. Firmware names must match linux-firmware or platform-provided firmware.

## Risks
Incorrect chip IDs can bind the wrong GPU generation. Firmware filenames are hardware-specific; A225 explicitly notes support only for msm8960v3 because v2 needed special firmware. Wrong GMEM size affects command submission and rendering correctness.

## Test signals
Probe logs for A200/A220/A225, successful firmware loading, correct GMEM size exposure, GPU idle timeout behavior, and rendering tests on the i.MX51 128 KiB GMEM variant are key signals.
