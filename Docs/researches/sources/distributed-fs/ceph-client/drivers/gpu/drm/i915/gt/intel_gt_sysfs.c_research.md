# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_sysfs.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_sysfs.c

### Purpose
`intel_gt_sysfs.c` creates per-GT sysfs kobjects and bridges legacy parent-device GT PM attributes with newer `gt/gtN` objects.

### Important APIs, Types, And Functions
Public functions are `is_object_gt()`, `intel_gt_sysfs_get_drvdata()`, `intel_gt_sysfs_register()`, and `intel_gt_sysfs_unregister()`. It also defines the `id` attribute and `kobj_gt_type`.

### Control Flow
Registration first creates legacy PM sysfs files on the parent device for root GT only, then initializes `gt->sysfs_gt` under `i915->sysfs_gt` as `gtN`, creates a `.defaults` child kobject, and initializes PM sysfs under the per-GT object. Unregister releases `.defaults` and the GT kobject. `intel_gt_sysfs_get_drvdata()` detects whether the caller is a `gtN` object or the parent device and returns the appropriate GT.

### State, Persistence, And Dependencies
State lives in `gt->sysfs_gt` and `gt->sysfs_defaults`. Dependencies include Linux kobjects/sysfs, DRM device objects, i915 sysfs helpers, GT PM sysfs, and GT id state.

### Integration Points
Called from GT driver registration/unregistration. PM sysfs code uses its object detection and drvdata helper to serve both ABI locations.

### Risks
Kobject lifetimes must be balanced even on partial registration failure. Name-based `is_object_gt()` assumes GT sysfs object names begin with `gt`. Legacy parent attributes intentionally aggregate root/all-GT behavior, so callers must use the helper rather than assuming private data type.

### Test Signals
Sysfs layout checks for `/gt/gt0`, optional `/gt/gt1`, `.defaults`, legacy parent power files, correct `id`, and clean unregister are important.
