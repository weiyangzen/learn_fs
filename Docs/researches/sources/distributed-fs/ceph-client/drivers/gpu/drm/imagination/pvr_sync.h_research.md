<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_sync.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_sync.h

Purpose: Declares the PowerVR synchronization helper API and the signal-cache object used during job submission.

Important APIs/types/functions: Defines `struct pvr_sync_signal` with syncobj handle, timeline point, syncobj reference, optional `dma_fence_chain`, and active fence. Declares cleanup, signal collection, fence update/push, and dependency-addition helpers.

Control flow: No implementation flow; documents the multi-step lifecycle used by submission code.

State and persistence behavior: `struct pvr_sync_signal` is an in-memory per-submission cache and reference holder for syncobj updates. It is not persistent beyond submission cleanup.

Dependencies: Forward-declares xarray, DRM file, DRM scheduler job, and PowerVR file structures; includes the PowerVR UAPI header.

Integration points: Included by queue/job submission code that processes `drm_pvr_sync_op` arrays.

Risks: Callers must run cleanup exactly once for arrays that may contain allocated signals. They also must preserve the collect/update/push order so syncobj state is not published before job fences exist.

Test signals: Build-time API coverage and runtime job submission with both signal and wait operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_sync.h -->
