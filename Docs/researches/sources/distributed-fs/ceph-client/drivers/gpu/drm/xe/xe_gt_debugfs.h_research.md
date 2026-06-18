# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_debugfs.h

## Purpose
Declares GT debugfs registration and common DRM info-list show callbacks.

## Important APIs
- `xe_gt_debugfs_register(struct xe_gt *gt)` installs the per-GT debugfs tree.
- `xe_gt_debugfs_simple_show` delegates to a GT printer stored in `drm_info_list.data`.
- `xe_gt_debugfs_show_with_rpm` wraps the simple callback with runtime PM.

## Integration and Risks
The shared callbacks are used by GT and SR-IOV debugfs files. Callers must set up dentry private data and `drm_info_list.data` consistently or the helper will warn and return `-EINVAL`.
