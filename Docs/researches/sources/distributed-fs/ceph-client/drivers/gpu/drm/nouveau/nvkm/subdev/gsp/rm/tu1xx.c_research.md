<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/tu1xx.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/tu1xx.c

## Purpose
Defines the static RM GPU class table for TU1xx/Turing GSP-RM operation. It names display, usermode, FIFO channel, copy, graphics, and video engine classes exposed to RM allocation paths.

## Important APIs, Types, And Functions
Important object is const struct nvkm_rm_gpu tu1xx_gpu. Fields include display root/caps/core/window/immediate/cursor classes, TURING_USERMODE_A, TURING_CHANNEL_GPFIFO_A plus tu102_chan_doorbell_handle, TURING_DMA_COPY_A, graphics class set, NVC4B0_VIDEO_DECODER, and NVC4B7_VIDEO_ENCODER.

## Control Flow
There is no control flow. tu102/tu116 GSP function tables point rm.gpu at tu1xx_gpu so RM allocation code can choose the correct class IDs for objects and channels.

## State, Persistence, Dependencies, And Integration
State is immutable class metadata. Dependencies are gpu.h, engine/fifo/priv.h, and nvif/class.h. Integration points are Turing GSP firmware interface entries, channel allocation, display channel allocation, and GR/video engine object creation.

## Risks And Test Signals
Risks: wrong class IDs cause RM object allocation failure or incompatible pushbuffer/channel behavior. Test signals include Turing display channel creation, GPFIFO channel startup, CE/GR/NVDEC/NVENC object allocation, and doorbell writes using the expected handle format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/tu1xx.c -->
