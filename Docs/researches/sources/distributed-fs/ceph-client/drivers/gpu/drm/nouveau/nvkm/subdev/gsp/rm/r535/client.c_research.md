<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/client.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/client.c

## Purpose
Implements R535 RM root client allocation.

## Important APIs, Types, And Functions
Defines `r535_gsp_client_ctor` and exports `r535_client`.

## Control Flow
The constructor allocates an `NV01_ROOT` object with `NV0000_ALLOC_PARAMETERS`, sets `hClient` to the chosen client handle and `processID` to all bits set, then submits the allocation.

## State And Persistence
The root RM client object persists in `client->object` until the generic client destructor frees it.

## Dependencies And Integration Points
Called by `nvkm_gsp_client_ctor`; uses R535 allocation wrappers and NVRM client definitions.

## Risks And Edge Cases
Failure to allocate the root client prevents all child RM objects. Process ID is synthetic and must be acceptable to RM firmware.

## Test Signals
Successful RM client constructor and later child device/subdevice allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/client.c -->
