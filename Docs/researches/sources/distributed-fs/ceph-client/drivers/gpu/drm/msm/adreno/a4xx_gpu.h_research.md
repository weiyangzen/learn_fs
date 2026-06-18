# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a4xx_gpu.h

## Purpose
`a4xx_gpu.h` declares the A4xx generation wrapper and function table used by catalog registration and runtime code.

## Important APIs, Types, And Functions
`struct a4xx_gpu` embeds `struct adreno_gpu base` and includes `struct adreno_ocmem ocmem`. `to_a4xx_gpu()` recovers the wrapper from an Adreno base pointer. `a4xx_gpu_funcs` is exported for catalog entries.

## Control Flow
The header has no executable flow. It establishes the static type layout and imports generated A4xx register definitions.

## State And Persistence
The persistent state declared here is the common Adreno object plus optional OCMEM allocation state. Runtime PM, firmware, ring, and register state are in the embedded/common structures.

## Dependencies And Integration Points
It includes `adreno_gpu.h`, applies the ROP macro workaround before `a4xx.xml.h`, and is consumed by `a4xx_gpu.c` and `a4xx_catalog.c`.

## Risks
The `base` field must remain first. Include-order macro conflicts with framebuffer ROP definitions are handled locally and can reappear if generated XML inclusion is moved.

## Test Signals
Build coverage plus successful A4xx probe/teardown are the primary signals, especially OCMEM initialization and cleanup through `to_a4xx_gpu`.
