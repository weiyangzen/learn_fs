# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_idle_types.h

## Purpose
Defines the idle state enum and `struct xe_gt_idle` used by GT idle sysfs and power management.

## Important Types
- `enum xe_gt_idle_state` distinguishes active C0, idle C6, and unknown state.
- `struct xe_gt_idle` stores name, powergate mask, residency multiplier, extended residency counters, lock, and GuC PC function pointers for state/residency reads.

## State and Integration
The struct is embedded in `struct xe_gt`. Its counters are updated under `raw_spinlock_t` to make residency reads safe against concurrent sysfs/PMU access.

## Risks and Test Signals
Function pointers must be initialized before any sysfs/PMU read. Residency counters depend on monotonic hardware counter reads and wrap handling in `xe_gt_idle.c`.
