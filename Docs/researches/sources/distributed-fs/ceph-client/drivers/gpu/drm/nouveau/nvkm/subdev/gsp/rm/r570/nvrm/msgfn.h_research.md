<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/msgfn.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/msgfn.h

## Purpose
Defines the GSP event IDs used by the host message notification path. It maps symbolic event names to the 0x1000-series values emitted by GSP-RM.

## Important APIs, Types, And Functions
Important entries include GSP_INIT_DONE, POST_EVENT, RC_TRIGGERED, MMU_FAULT_QUEUED, OS_ERROR_LOG, UCODE_LIBOS_PRINT, DISPLAY_MODESET, GSP_LOCKDOWN_NOTICE, UPDATE_GSP_TRACE, GSP_POST_NOCAT_RECORD, FECS_ERROR, RECOVERY_ACTION, and NUM_EVENTS.

## Control Flow
No executable flow exists. Code registers callbacks for selected event IDs with r535_gsp_msg_ntfy_add and the message receiver dispatches incoming GSP events by these values.

## State, Persistence, Dependencies, And Integration
State is event identity only. Dependencies are nvrm/nvtypes.h. Integration points are r570_gsp_drop_post_nocat_record, FIFO RC handling, OS error logging, display event handling, and GSP boot/init notification.

## Risks And Test Signals
Risks: enum drift drops or misroutes asynchronous firmware notifications. Test signals include GSP_INIT_DONE delivery, RC_TRIGGERED processing, lockdown/nocat filtering at expected debug levels, and absence of unknown event spam.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/msgfn.h -->
