# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_freq.h

## Purpose
Declares GT frequency sysfs initialization.

## Important API
- `xe_gt_freq_init(struct xe_gt *gt)` creates and wires the `freq0` sysfs interface when GuC PC is available.

## Integration and Risks
The API must be called after GT sysfs and GuC PC state are ready. It returns errors for kobject/file creation and can be skipped by implementation for platforms that disable GuC PC.
