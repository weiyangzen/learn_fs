<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/nvdec.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/nvdec.c

## Purpose
Creates RM-backed NVDEC engine wrappers.

## Important APIs, Types, And Functions
Defines `nvkm_rm_nvdec_dtor` and exports `nvkm_rm_nvdec_new`.

## Control Flow
Constructor calls `nvkm_rm_engine_ctor` with the generation NVDEC class and installs the result into `device->nvdec[inst]`. Destructor frees the engine function table.

## State And Persistence
Persists an NVKM engine object and function table while the engine exists.

## Dependencies And Integration Points
Depends on generic RM engine construction and `rm->gpu->nvdec.class`.

## Risks And Edge Cases
Missing or zero class IDs cause unusable NVDEC allocation paths. Instance bounds are checked by caller `nvkm_rm_engine_new`.

## Test Signals
Successful NVDEC engine creation and userspace decoder object allocation/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/nvdec.c -->
