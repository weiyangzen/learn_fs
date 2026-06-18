# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a3xx_gpu.h

## Purpose
`a3xx_gpu.h` declares the A3xx GPU wrapper and function table used by the Adreno catalog and runtime implementation.

## Important APIs, Types, And Functions
`struct a3xx_gpu` embeds `struct adreno_gpu base` and contains an `adreno_ocmem` member for variants using OCMEM as GMEM. `to_a3xx_gpu()` performs the container cast. `a3xx_gpu_funcs` is the exported generation function table.

## Control Flow
The header has no executable flow. It defines the type relationship that lets common Adreno code operate on `msm_gpu` while A3xx runtime code can recover generation-local OCMEM state.

## State And Persistence
The declared persistent state is the common Adreno base plus optional OCMEM allocation metadata. Firmware, rings, and register tables live in the embedded base.

## Dependencies And Integration Points
It includes `adreno_gpu.h`, undefines framebuffer ROP macros before including generated `a3xx.xml.h`, and is consumed by `a3xx_gpu.c` and `a3xx_catalog.c`.

## Risks
`base` must remain first for `to_a3xx_gpu`. Generated XML naming conflicts are managed by the ROP undef workaround; removing it can create compile breakage depending on include order.

## Test Signals
Compile coverage and successful A3xx probe are the primary signals. Runtime signals include correct OCMEM cleanup through `to_a3xx_gpu` during teardown.
