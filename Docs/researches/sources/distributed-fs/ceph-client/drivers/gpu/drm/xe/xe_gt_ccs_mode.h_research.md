# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_ccs_mode.h

## Purpose
Declares CCS mode programming/sysfs helpers and a small predicate for whether CCS mode is meaningful on a GT.

## Important APIs
- `xe_gt_apply_ccs_mode(struct xe_gt *gt)` writes the currently selected CCS mode to hardware.
- `xe_gt_ccs_mode_sysfs_init(struct xe_gt *gt)` installs sysfs controls.
- `xe_gt_ccs_mode_enabled` returns true when more than one CCS instance is present.

## Integration and Risks
The inline predicate depends on `CCS_INSTANCES(gt)` from `xe_gt.h`; callers should only expose or apply mode when multiple compute engines exist and must still respect SR-IOV VF restrictions in implementation.
