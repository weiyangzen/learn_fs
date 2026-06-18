# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_pm.h

### Purpose
`intel_gt_pm.h` exposes GT wakeref helpers and PM lifecycle declarations.

### Important APIs, Types, And Functions
It defines inline helpers `intel_gt_pm_is_awake()`, get/put tracked and untracked wakeref routines, `intel_gt_pm_get_if_awake()`, async put helpers, `with_intel_gt_pm`, `with_intel_gt_pm_if_awake`, `intel_gt_pm_wait_for_idle()`, `is_mock_gt()`, and declarations for init/fini/suspend/resume/runtime PM and awake-time retrieval.

### Control Flow
Callers acquire GT wakerefs before hardware access or submission and release them synchronously or asynchronously. Conditional helpers run code only if the GT is already awake. Lifecycle functions are called by probe, driver teardown, runtime PM, and system PM.

### State, Persistence, And Dependencies
The header manipulates `gt->wakeref` and, for mock detection, `gt->awake`. It depends on `intel_wakeref` and GT types.

### Integration Points
Used throughout i915 GT, engine, debugfs, sysfs, and runtime PM code to keep GT hardware powered while accessing registers or submitting work.

### Risks
Unbalanced wakeref get/put calls keep the GT awake or allow premature suspend. Tracked handles must be passed back to the matching put helper.

### Test Signals
Wakeref debug tracking, runtime PM autosuspend, lockdep, and tests that exercise get-if-awake and async put paths validate this header's contracts.
