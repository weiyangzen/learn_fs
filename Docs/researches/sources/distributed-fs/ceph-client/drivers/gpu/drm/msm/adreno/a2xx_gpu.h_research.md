# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a2xx_gpu.h

## Purpose
`a2xx_gpu.h` declares the A2xx-specific GPU wrapper, generation register definitions, and the GPUMMU interface used by `a2xx_gpu.c`.

## Important APIs, Types, And Functions
The central type is `struct a2xx_gpu`, embedding `struct adreno_gpu base` and adding `pm_enabled` plus `protection_disabled`. `to_a2xx_gpu()` converts from `adreno_gpu` to the generation wrapper. The header exports `a2xx_gpu_funcs`, `a2xx_gpummu_new`, and `a2xx_gpummu_params`.

## Control Flow
The header has no runtime control flow. It defines the declarations that allow catalog/platform code to select `a2xx_gpu_funcs`, allow the runtime file to cast into `struct a2xx_gpu`, and allow VM creation to instantiate/configure the A2xx GPUMMU.

## State And Persistence
The only declared persistent state is the per-device A2xx wrapper. `protection_disabled` is especially important because firmware probing can set it and subsequent ME initialization will skip protected mode.

## Dependencies And Integration Points
It includes `adreno_gpu.h`, undefines `ROP_COPY` and `ROP_XOR` before including generated `a2xx.xml.h`, and forward-declares the MMU helper API consumed by `a2xx_gpu.c`.

## Risks
The header couples A2xx runtime code to the generated XML register namespace and the old GPUMMU implementation. Any change to `struct a2xx_gpu` must preserve `base` as the first field for `container_of`. Prototype drift would break VM setup or firmware/protection handling.

## Test Signals
Compile coverage is the primary signal. Runtime signals include successful casts through `to_a2xx_gpu`, successful A2xx VM creation through `a2xx_gpummu_new`, and protected-mode behavior following `protection_disabled`.
