<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/fbsr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/fbsr.h

## Purpose
Defines the RM control payload for internal framebuffer suspend/resume initialization. It binds an RM client and system-memory object to the sysmem suspend/resume data area used across low-power transitions.

## Important APIs, Types, And Functions
Important API is NV2080_CTRL_CMD_INTERNAL_FBSR_INIT and NV2080_CTRL_INTERNAL_FBSR_INIT_PARAMS with hClient, hSysMem, bEnteringGcoffState, and aligned sysmemAddrOfSuspendResumeData.

## Control Flow
No local control flow exists. FBSR code fills this struct during suspend entry so GSP-RM can save or restore video memory state and know whether the transition is GC-off related.

## State, Persistence, Dependencies, And Integration
State is the sysmem physical address and RM handles supplied by the caller. Dependencies are nvrm/nvtypes.h. Integration points are nvkm_rm_api_fbsr, GSP SR metadata in gsp.h, and r570_gsp_set_rmargs resume flags.

## Risks And Test Signals
Risks: wrong sysmem address or handle corrupts suspend/resume state; GC-off flag mismatch may select the wrong firmware path. Test signals are successful runtime/system suspend-resume with preserved allocations and no FBSR_INIT control failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/fbsr.h -->
