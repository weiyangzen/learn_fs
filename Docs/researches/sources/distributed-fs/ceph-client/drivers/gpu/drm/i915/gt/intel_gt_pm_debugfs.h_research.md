# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm_debugfs.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm_debugfs.h

### Purpose
`intel_gt_pm_debugfs.h` declares the GT PM debugfs registration and helper interfaces.

### Important APIs, Types, And Functions
It declares `intel_gt_pm_debugfs_register()`, `intel_gt_pm_frequency_dump()`, and forcewake-user open/release helpers.

### Control Flow
Core GT debugfs calls the registration function. Other debugfs layers may use the forcewake helpers to share the same user-forcewake accounting.

### State, Persistence, And Dependencies
The header stores no state. It depends on forward declarations for GT, dentry, and DRM printer.

### Integration Points
Connects PM diagnostics with core GT debugfs and any upper-level debugfs files that need forcewake behavior.

### Risks
Callers must pair forcewake open/release helpers or leak a GT PM/forcewake reference.

### Test Signals
Compile coverage and forcewake reference balance during debugfs open/release validate the interface.
