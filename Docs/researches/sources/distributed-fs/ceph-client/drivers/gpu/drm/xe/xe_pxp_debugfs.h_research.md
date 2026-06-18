<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_debugfs.h

Purpose: declares the PXP debugfs registration hook.

Important API: `xe_pxp_debugfs_register(struct xe_pxp *pxp)` is the single entry point and is expected to be called only when PXP support is being exposed through DRM debugfs.

Dependencies and risks: forward declares `struct xe_pxp`; there is no stub here, so build integration must only include/call it where the implementation is available. Test signal is the presence of `pxp/info` and `pxp/terminate` under the DRM minor debugfs root.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_debugfs.h -->
