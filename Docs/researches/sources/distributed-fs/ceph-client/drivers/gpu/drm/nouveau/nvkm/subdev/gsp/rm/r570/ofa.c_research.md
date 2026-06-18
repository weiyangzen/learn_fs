<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/ofa.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/ofa.c

## Purpose
Implements the R570 RM engine allocator for OFA objects. It adapts the generic nvkm_rm_api_engine allocation hook to the R570 NV_OFA_ALLOCATION_PARAMETERS payload.

## Important APIs, Types, And Functions
Main API is r570_ofa_alloc(parent, handle, oclass, inst, ofa), exported through const struct nvkm_rm_api_engine r570_ofa. It uses nvkm_gsp_rm_alloc_get and nvkm_gsp_rm_alloc_wr.

## Control Flow
Allocation requests reserve an RM payload/object under the parent, fill size and engineInstance, then write the allocation to GSP-RM. IS_ERR is treated as a warning and returned as PTR_ERR.

## State, Persistence, Dependencies, And Integration
State is the initialized nvkm_gsp_object for the OFA engine and the firmware-side allocation. Dependencies are rm/engine.h and nvrm/ofa.h. Integration points are r570_api.ofa, engine object creation, and R570 engine index translation for OFA instances.

## Risks And Test Signals
Risks: no local validation of inst beyond RM failure; WARN_ON on allocation-get errors may be noisy if absent hardware is probed incorrectly. Test signals include successful OFA allocation for valid instances and clean -errno propagation for unsupported classes/instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/ofa.c -->
