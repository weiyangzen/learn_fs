<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/fifo.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/fifo.h

## Purpose
Provides R570 RM payloads and flags for GPFIFO channel allocation, memory descriptors, runqueue/privilege/channel options, RC-triggered event payloads, constructed falcon discovery, and active-channel scheduling control.

## Important APIs, Types, And Functions
Key types include NV_MEMORY_DESC_PARAMS, NV_CHANNEL_ALLOC_PARAMS/NV_CHANNELGPFIFO_ALLOCATION_PARAMETERS, NVOS04_FLAGS_* channel bitfields, ErrorNotifierType, NV_KERNELCHANNEL_ALLOC_INTERNALFLAGS_* fields, rpc_rc_triggered_v17_02, NV2080_CTRL_GPU_CONSTRUCTED_FALCON_INFO, NV2080_CTRL_GPU_GET_CONSTRUCTED_FALCON_INFO_PARAMS, and NV2080_CTRL_INTERNAL_FIFO_TOGGLE_ACTIVE_CHANNEL_SCHEDULING_PARAMS.

## Control Flow
No executable flow is present. FIFO allocation code fills memory descriptors for instance, USERD, RAMFC, method buffer, notifier memory, GP FIFO offset/entries, VASpace handle, engine type, cid, and subdevice mask before asking GSP-RM to allocate a channel. RC event handlers decode rpc_rc_triggered_v17_02 and may call Nouveau recovery logic by chid.

## State, Persistence, Dependencies, And Integration
State is command payload memory and firmware event payloads. Dependencies are nvrm/nvtypes.h and R570 NV2080 engine constants. Integration points are nvkm_rm_api_fifo, channel object allocation, fault recovery notification, constructed falcon context sizing, and scheduler quiesce paths.

## Risks And Test Signals
Risks: packed flexible rcJournalBuffer must be length-checked by consumers; channel memory aperture/cache fields must match actual nvkm_memory backing; flag drift can change privilege/security behavior. Test signals include channel creation/destruction on graphics/copy/video engines, RC recovery for faulted chids, scheduler toggle controls, and constructed falcon info queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/fifo.h -->
