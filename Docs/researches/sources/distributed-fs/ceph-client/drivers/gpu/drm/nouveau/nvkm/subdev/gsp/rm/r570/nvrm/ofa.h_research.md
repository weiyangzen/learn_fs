<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/ofa.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/ofa.h

## Purpose
Defines the Optical Flow Accelerator allocation payload used by the R570 OFA engine allocation hook.

## Important APIs, Types, And Functions
Important type is NV_OFA_ALLOCATION_PARAMETERS with size, prohibitMultipleInstances, and engineInstance.

## Control Flow
No control flow exists. r570_ofa_alloc creates this payload, sets size to sizeof payload and engineInstance to the requested instance, then submits the RM allocation.

## State, Persistence, Dependencies, And Integration
State is caller-owned allocation payload. Dependencies are nvrm/nvtypes.h. Integration points are r570_ofa in ofa.c and the generic nvkm_rm_api_engine allocator path.

## Risks And Test Signals
Risks: wrong size or instance value can make RM reject OFA allocation or allocate the wrong hardware instance. Test signals are OFA object allocation on chips exposing OFA0/OFA1 and correct failure on absent instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/ofa.h -->
