<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/nvenc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/nvenc.c

## Purpose
Creates RM-backed NVENC engine wrappers.

## Important APIs, Types, And Functions
Defines `nvkm_rm_nvenc_dtor` and exports `nvkm_rm_nvenc_new`.

## Control Flow
Constructor delegates to `nvkm_rm_engine_ctor` with the generation NVENC class and stores the engine in `device->nvenc[inst]`. Destructor frees the generated function table.

## State And Persistence
The engine object persists in the device NVENC array until teardown.

## Dependencies And Integration Points
Depends on generic RM engine helpers and `rm->gpu->nvenc.class`.

## Risks And Edge Cases
Devices without NVENC class support should not route here. Bad class IDs fail RM allocations.

## Test Signals
Successful NVENC engine creation and video encoder class allocation/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/nvenc.c -->
