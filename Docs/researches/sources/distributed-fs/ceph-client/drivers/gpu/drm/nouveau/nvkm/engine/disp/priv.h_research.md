<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/priv.h

## Purpose

`priv.h` is the private display-engine contract. It defines `struct nvkm_disp_func`, constructor prototypes, shared supervisor/init/intr helpers, and user object constructors consumed by all display generation files.

## Important APIs, Types, And Functions

`struct nvkm_disp_func` contains lifecycle hooks (`dtor`, `oneinit`, `init`, `fini`, `intr`, `super`), optional interrupt error handling, event function pointer, resource count/new callbacks for windows/heads/DACs/SORs/PIORs, RAMHT size, root class, and a variable user-class table. The file declares `nvkm_disp_ctor()`, `nvkm_disp_new_()`, `r535_disp_new()`, `nvkm_disp_vblank()`, NV50/GF119/GV100/TU102 shared helpers, channel event functions, and user constructors for display/connector/output/head.

## Control Flow

Generation files build static `nvkm_disp_func` tables and pass them to `nvkm_disp_new_()` or `r535_disp_new()`. Generic display construction later calls oneinit/init/fini/intr through this table. `udisp.c` enumerates `func->user[]` to expose generation-specific NVIF classes.

## State And Persistence Behavior

The header does not own state, but its function table determines which resource lists, RAMHT sizes, user classes, event hooks, and supervisor behavior are installed into each `struct nvkm_disp` instance.

## Dependencies And Integration Points

It includes public `engine/disp.h` and enum support, forward declares display private objects, and bridges classic nouveau display implementations with GSP/R535-backed display construction.

## Risks And Edge Cases

The user-class array is open-ended and must be terminated. Missing callbacks are meaningful for older generations, so callers must respect optionality. A generation table that mixes incompatible init/intr/super hooks with resource counts can expose wrong MMIO layouts.

## Test Signals

Test through successful build, display engine probe, root/user class enumeration, vblank events, and correct routing to GSP-backed `r535_disp_new()` on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/priv.h -->
