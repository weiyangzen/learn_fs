# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_idle.h

## Purpose
Declares GT idle, powergating, C6, debug printing, and residency APIs.

## Important APIs
- `xe_gt_idle_init` initializes `struct xe_gt_idle` and sysfs.
- `xe_gt_idle_enable_pg` / `xe_gt_idle_disable_pg` control powergating bits.
- `xe_gt_idle_enable_c6` / `xe_gt_idle_disable_c6` control RC6/C6.
- `xe_gt_idle_pg_print` emits debugfs powergate state.
- `xe_gt_idle_residency_msec` returns extended residency in milliseconds.

## Integration and Risks
The header includes `xe_gt_idle_types.h` so callers can embed/use the state object. Most operations require valid GT memory/MMIO access; implementation skips SR-IOV VFs for hardware programming.
