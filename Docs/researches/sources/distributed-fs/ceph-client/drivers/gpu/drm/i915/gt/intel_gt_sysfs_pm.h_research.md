# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_sysfs_pm.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_sysfs_pm.h

### Purpose
`intel_gt_sysfs_pm.h` declares GT PM sysfs initialization.

### Important APIs, Types, And Functions
It declares `intel_gt_sysfs_pm_init(struct intel_gt *gt, struct kobject *kobj)`.

### Control Flow
GT sysfs registration calls this function once for the legacy parent object on root GT and once for each per-GT kobject.

### State, Persistence, And Dependencies
The header stores no state. It includes kobject and GT type declarations.

### Integration Points
Connects core GT sysfs object creation with PM/RPS/RC6/SLPC attribute registration.

### Risks
No direct runtime risk, but callers must pass the correct kobject type because the implementation changes behavior for legacy versus `gtN` objects.

### Test Signals
Build coverage and expected sysfs files under both legacy and per-GT paths validate the interface.
