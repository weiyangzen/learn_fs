<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/client.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/client.h

## Purpose
Defines the minimal R570 RM root-client allocation contract used by Nouveau's RM allocation layer. The file is an imported NVIDIA open-gpu-kernel-modules 570.144 ABI excerpt rather than executable logic.

## Important APIs, Types, And Functions
Important definitions are NV01_ROOT, NV_PROC_NAME_MAX_LENGTH, and NV0000_ALLOC_PARAMETERS with hClient, processID, processName, and aligned pOsPidInfo. The comment noting hClient must remain first is part of the ABI contract.

## Control Flow
There is no runtime control flow in this header. Consumers allocate a root/client object by filling NV0000_ALLOC_PARAMETERS and passing it through the GSP-RM allocation API selected by r570_client/r535_alloc.

## State, Persistence, Dependencies, And Integration
State is entirely caller-owned payload memory. Dependencies are nvrm/nvtypes.h for NvHandle, NvU32, NvP64, and alignment macros. Integration points are the R570 client ctor declared in rm.h and RM alloc RPCs.

## Risks And Test Signals
Risks: field order or size drift breaks RM allocation. Test signals are compile-time struct compatibility and successful creation/destruction of internal and user RM clients under 570.144 firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/client.h -->
