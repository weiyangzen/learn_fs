# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_sysfs.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_sysfs.h

### Purpose
`intel_gt_sysfs.h` exposes helpers for GT sysfs object detection, kobject-to-GT conversion, registration, and private-data lookup.

### Important APIs, Types, And Functions
It declares `is_object_gt()`, `intel_gt_sysfs_register()`, `intel_gt_sysfs_unregister()`, `intel_gt_sysfs_get_drvdata()`, and inline `kobj_to_gt()`. It also declares `kobj_to_i915()`.

### Control Flow
PM sysfs show/store functions use `intel_gt_sysfs_get_drvdata()` to support both per-GT kobjects and legacy parent-device attributes.

### State, Persistence, And Dependencies
The header stores no state but assumes `struct intel_gt` contains `sysfs_gt`. It depends on kobject types, ctype, GEM bug checks, and GT types.

### Integration Points
Used by GT sysfs core and PM sysfs implementation.

### Risks
`kobj_to_gt()` is only valid for kobjects embedded in `struct intel_gt`; callers must use object detection when handling legacy parent-device attributes.

### Test Signals
Compile coverage and sysfs reads/writes from both legacy and per-GT paths validate the contract.
