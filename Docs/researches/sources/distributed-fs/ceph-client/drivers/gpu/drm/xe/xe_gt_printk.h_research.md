# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_printk.h

## Purpose
Defines GT-scoped logging macros and DRM printer constructors that prefix messages with GT identity through tile-aware logging.

## Important APIs and Macros
- Logging macros: `xe_gt_err`, `xe_gt_err_once`, `xe_gt_err_ratelimited`, `xe_gt_warn`, `xe_gt_notice`, `xe_gt_info`, and `xe_gt_dbg`.
- Warning macros: `xe_gt_WARN`, `xe_gt_WARN_ONCE`, `xe_gt_WARN_ON`, and `xe_gt_WARN_ON_ONCE`.
- Printer constructors: `xe_gt_err_printer`, `xe_gt_info_printer`, and `xe_gt_dbg_printer`.

## Control Flow and State
Macros format messages as `GT%u: ...` and delegate to tile logging. Printer callbacks recover `struct xe_gt *` from `drm_printer.arg`; the debug printer preserves origin by redirecting through `xe_tile_dbg_printer`.

## Dependencies and Integration Points
Used throughout GT, GSC, SR-IOV, MCR, and debug code for consistent log attribution. Depends on `xe_gt_types.h` and `xe_tile_printk.h`.

## Risks and Test Signals
- Callers must pass a valid `struct xe_gt *`; macros dereference `gt->info.id` and `gt->tile`.
- Printer callbacks are useful when dumping KLVs or debug state through existing logging levels.
