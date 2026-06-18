# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_clock.h

## Purpose
Declares GT clock initialization and interval conversion helpers.

## Important APIs
- `xe_gt_clock_init(struct xe_gt *gt)` initializes clock fields in `gt->info`.
- `xe_gt_clock_interval_to_ms(struct xe_gt *gt, u64 count)` converts GT ticks to milliseconds.

## Integration and Risks
Callers must ensure `xe_gt_clock_init` has run and produced a nonzero reference clock before using conversion. The header keeps dependencies minimal with only `linux/types.h` and a GT forward declaration.
