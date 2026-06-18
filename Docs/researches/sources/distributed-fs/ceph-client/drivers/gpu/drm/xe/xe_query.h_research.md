<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_query.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_query.h

Purpose: declares the Xe query ioctl entry point.

Important API: `xe_query_ioctl(struct drm_device *dev, void *data, struct drm_file *file)` is wired into DRM ioctl handling and interprets `data` as `struct drm_xe_device_query`.

Dependencies and risks: forward declares DRM device/file types and keeps query implementation internal to `xe_query.c`. Tests should exercise the ioctl through DRM uAPI rather than this header directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_query.h -->
