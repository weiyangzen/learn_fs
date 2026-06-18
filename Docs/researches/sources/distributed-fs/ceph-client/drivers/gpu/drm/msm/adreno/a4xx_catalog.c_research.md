# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a4xx_catalog.c

## Purpose
`a4xx_catalog.c` registers the supported Adreno 4xx devices with static firmware, GMEM, revision, and function-table metadata.

## Important APIs, Types, And Functions
The file defines `a4xx_gpus[]` and publishes it with `DECLARE_ADRENO_GPULIST(a4xx)`. Entries cover A405, A420, and A430, using `ADRENO_CHIP_IDS`, `ADRENO_4XX`, `.revn`, PM4/PFP firmware names, `.gmem`, `.inactive_period`, and `.funcs = &a4xx_gpu_funcs`.

## Control Flow
There is no runtime algorithm. The shared Adreno catalog lookup selects these immutable entries during probe and stores them in the runtime `adreno_gpu`.

## State And Persistence
The table values persist as `adreno_gpu->info` and influence firmware loading, GMEM range setup, register table selection, and helper predicates such as `adreno_is_a405`, `adreno_is_a420`, and `adreno_is_a430`.

## Dependencies And Integration Points
It includes `adreno_gpu.h` and `a4xx_gpu.h`. Runtime code in `a4xx_gpu.c` consumes the revision and GMEM values and depends on the common catalog macros to expose the list.

## Risks
Incorrect catalog metadata will select wrong firmware or runtime workarounds. A405 shares A420 firmware but has a distinct register table and no CCU path, so revision accuracy matters.

## Test Signals
Expected signals are exact chip ID matching, correct firmware request names, correct A405/A420/A430 branch selection in `a4xx_hw_init`, and GMEM sizes matching hardware capabilities.
