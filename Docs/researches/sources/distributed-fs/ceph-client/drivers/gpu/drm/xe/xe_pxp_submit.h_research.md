<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_submit.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_submit.h

Purpose: declares the internal PXP submission helper interface between the PXP state machine and command-emission implementation.

Important APIs: allocation/lifetime functions `xe_pxp_allocate_execution_resources()` and `xe_pxp_destroy_execution_resources()`; firmware/VCS submission functions `xe_pxp_submit_session_init()`, `xe_pxp_submit_session_termination()`, and `xe_pxp_submit_session_invalidation()`.

Dependencies and risks: forward declares `struct xe_pxp` and `struct xe_pxp_gsc_client_resources`; consumers must pass initialized resources from `xe_pxp_init()`. Tests should verify callers do not submit after destroy and handle negative errno returns from all command paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_submit.h -->
