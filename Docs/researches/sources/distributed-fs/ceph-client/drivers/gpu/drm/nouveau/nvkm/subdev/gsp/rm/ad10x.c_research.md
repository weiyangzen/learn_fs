<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/ad10x.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/ad10x.c

## Purpose
Defines Ada AD10x RM class IDs and FIFO doorbell behavior for RM-backed Nouveau objects.

## Important APIs, Types, And Functions
Exports `ad10x_gpu` as `struct nvkm_rm_gpu`, filling display, usermode, FIFO channel, CE, GR, NVDEC, NVENC, and OFA class IDs.

## Control Flow
No dynamic flow. RM engine/display/fifo constructors read this table when creating objects.

## State And Persistence
The table is immutable generation metadata.

## Dependencies And Integration Points
Uses NVIF class IDs and `tu102_chan_doorbell_handle`. Referenced by `ad102_gsp`.

## Risks And Edge Cases
Incorrect class IDs cause RM allocation failures or wrong engine classes exposed to userspace.

## Test Signals
Successful display channel creation, FIFO channel allocation, and CE/GR/video engine object allocation on AD10x.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/ad10x.c -->
