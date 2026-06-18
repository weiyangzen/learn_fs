# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_clock_utils.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_clock_utils.h

### Purpose
`intel_gt_clock_utils.h` exposes GT clock initialization, optional debug validation, and clock/PM interval conversion helpers.

### Important APIs, Types, And Functions
It declares `intel_gt_init_clock_frequency()`, `intel_gt_check_clock_frequency()`, `intel_gt_clock_interval_to_ns()`, `intel_gt_pm_interval_to_ns()`, `intel_gt_ns_to_clock_interval()`, and `intel_gt_ns_to_pm_interval()`.

### Control Flow
The debug check compiles to a no-op unless `CONFIG_DRM_I915_DEBUG_GEM` is enabled. Other callers use the conversion helpers after GT MMIO initialization has populated clock fields.

### State, Persistence, And Dependencies
The header stores no state and depends only on integer types plus a `struct intel_gt` forward declaration.

### Integration Points
Included by GT initialization, PM, RPS, debugfs, and code that converts hardware timestamp units.

### Risks
Callers must not use conversion helpers before initialization or when `clock_frequency` is zero.

### Test Signals
Build coverage with debug enabled/disabled and runtime checks on platforms with different timestamp sources are the key signals.
