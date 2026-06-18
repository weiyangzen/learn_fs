<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/handles.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/handles.h

## Purpose
Defines Nouveau-local RM object handle constants and encodings.

## Important APIs, Types, And Functions
Provides macros such as `NVKM_RM_CLIENT(id)`, `NVKM_RM_CLIENT_MASK`, `NVKM_RM_DEVICE`, `NVKM_RM_SUBDEVICE`, `NVKM_RM_DISP`, `NVKM_RM_VASPACE`, `NVKM_RM_CHAN(chid)`, and `NVKM_RM_THREED`.

## Control Flow
No runtime flow. Handles are embedded in RM allocation and free messages.

## State And Persistence
Handle values persist as identifiers for allocated RM objects until freed.

## Dependencies And Integration Points
Used by RM client, device, display, FIFO, GR, VMM, and engine code to create stable RM object hierarchies.

## Risks And Edge Cases
Handle collisions can corrupt RM object ownership. Client IDs must stay within `NVKM_RM_CLIENT_MASK`.

## Test Signals
No RM allocation conflicts, successful free of handles, and correct IDR client removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/handles.h -->
