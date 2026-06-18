<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/priv.h

## Purpose
Declares private GPIO function-table types and shared generation helper prototypes.

## Important APIs, Types, And Functions
Defines `nvkm_gpio(p)` and `struct nvkm_gpio_func` with line count, interrupt status/mask, drive, sense, and reset hooks. Declares `nvkm_gpio_new_` plus NV50/G94/GF119 helper functions reused across generations.

## Control Flow
No runtime flow; it is the compile-time contract between common base and generation files.

## State And Persistence
No state is stored here. Function tables persist inside constructed `struct nvkm_gpio` objects.

## Dependencies And Integration Points
Includes public `subdev/gpio.h`; generation implementations and `base.c` depend on it.

## Risks And Edge Cases
Hook signatures assume generation code maps line numbers and interrupt masks correctly. Missing mandatory hooks lead to null calls in the base layer.

## Test Signals
Compile/link success and correct dispatch through `gpio->func`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/priv.h -->
