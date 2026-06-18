<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/engine.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/engine.c

## Purpose
Provides generic RM-backed NVKM engine and engine-object construction for CE, GR, NVDEC, NVENC, NVJPG, and OFA engines.

## Important APIs, Types, And Functions
Defines `struct nvkm_rm_engine`, `struct nvkm_rm_engine_obj`, `nvkm_rm_engine_obj_new`, `nvkm_rm_engine_ctor`, `nvkm_rm_engine_new`, and internal object destructors/constructors.

## Control Flow
Engine construction builds an `nvkm_engine_func` with supported class entries, each using `nvkm_rm_engine_obj_ctor`. Object construction dispatches by engine type to the relevant RM API allocation hook or generic `nvkm_gsp_rm_alloc` for GR. `nvkm_rm_engine_new` maps requested NVKM engine type/instance to the device engine slot and generation class ID, special-casing GR and unsupported MiG GR instances.

## State And Persistence
Engine function tables and RM objects persist while engines/objects exist. Object destructors free RM handles.

## Dependencies And Integration Points
Depends on `nvkm_rm_gpu` class tables, FIFO channels, RM API engine allocators, and NVKM engine/object frameworks.

## Risks And Edge Cases
Instance bounds are checked for device arrays. Unsupported engine types return `-ENODEV`; GR instance other than 0 is ignored. Missing class IDs or RM API hooks cause allocation failures.

## Test Signals
Engine subdev creation, successful userspace object allocation for each class, and RM object free on destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/engine.c -->
