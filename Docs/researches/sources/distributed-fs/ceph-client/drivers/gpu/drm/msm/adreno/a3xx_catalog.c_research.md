# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a3xx_catalog.c

## Purpose
`a3xx_catalog.c` is the static device catalog for Adreno 3xx GPUs. It describes supported chip IDs, firmware filenames, GMEM size, inactive period, revision numbers where needed, and the function table used by the common Adreno discovery path.

## Important APIs, Types, And Functions
The file defines `static const struct adreno_info a3xx_gpus[]` and publishes it through `DECLARE_ADRENO_GPULIST(a3xx)`. Each entry uses `ADRENO_CHIP_IDS`, firmware slots `ADRENO_FW_PM4`/`ADRENO_FW_PFP`, `ADRENO_3XX`, GMEM sizes, optional `.revn`, and `.funcs = &a3xx_gpu_funcs`.

## Control Flow
There is no executable flow beyond static registration. At probe/catalog lookup time, the shared Adreno code matches a detected chip ID against this array and passes the selected `adreno_info` into platform/runtime initialization.

## State And Persistence
The table is immutable. Its values persist as `adreno_gpu->info` and drive firmware loading, GMEM range setup, revision checks, and runtime workarounds in `a3xx_gpu.c`.

## Dependencies And Integration Points
It includes `adreno_gpu.h` and `a3xx_gpu.h`. Runtime code consumes the resulting `adreno_info` through helpers such as `adreno_is_a305`, `adreno_is_a320`, and `adreno_is_a330`, and uses `.gmem` for GMEM register programming.

## Risks
Catalog errors cause wrong firmware, wrong GMEM size, or wrong generation dispatch. Several chip IDs collapse to shared firmware, while some entries use artificial `.revn` values for helper compatibility; changing them can break runtime branch selection.

## Test Signals
Probe logs should identify the intended A3xx variant, request the expected `a300_*` or `a330_*` firmware files, program the expected GMEM size, and route initialization through `a3xx_gpu_funcs`. Device-tree/platform matrices should confirm every listed chip ID matches exactly one entry.
