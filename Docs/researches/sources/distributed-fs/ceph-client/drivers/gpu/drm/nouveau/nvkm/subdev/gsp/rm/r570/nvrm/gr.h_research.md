<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/gr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/gr.h

## Purpose
Defines R570 graphics RM control payloads for context buffer discovery, GPC/TPC topology queries, a graphics scrubber workaround, and ZCULL information.

## Important APIs, Types, And Functions
Important definitions are NV2080_CTRL_INTERNAL_STATIC_GR_GET_CONTEXT_BUFFERS_INFO_PARAMS, NV2080_CTRL_INTERNAL_STATIC_GR_CONTEXT_BUFFERS_INFO, NV2080_CTRL_INTERNAL_ENGINE_CONTEXT_BUFFER_INFO, engine context property IDs, NV2080_CTRL_GPU_GET_FERMI_GPC_INFO_PARAMS, NV2080_CTRL_GPU_GET_FERMI_TPC_INFO_PARAMS, KGRAPHICS_SCRUBBER_HANDLE_* constants, NV2080_CTRL_INTERNAL_GR_INIT_BUG4208224_WAR_PARAMS, and NV2080_CTRL_GR_GET_ZCULL_INFO_PARAMS.

## Control Flow
There is no local control flow. GR code issues internal controls to fetch per-engine context-buffer size/alignment, query global GPC mask and per-GPC TPC masks, set up or tear down the scrubber workaround, and retrieve ZCULL geometry constraints.

## State, Persistence, Dependencies, And Integration
State lives in RM control payloads and then is copied into r535/r570 GR objects. Dependencies are nvrm/nvtypes.h and the RM control path. Integration points are r570_gr_gpc_mask/r570_gr_tpc_mask used by gsp.c, GR channel/context promotion, scrubber initialization, and ZCULL allocation setup.

## Risks And Test Signals
Risks: context-buffer enum count must match RM; topology masks are used to size GPU resources; scrubber handle constants must not collide. Test signals include correct GR unit counts, context promotion success, ZCULL info availability, and graphics workload startup after scrubber init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/gr.h -->
