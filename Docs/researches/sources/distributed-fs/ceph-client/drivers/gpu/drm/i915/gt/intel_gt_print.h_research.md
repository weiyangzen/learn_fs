# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_print.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_print.h

### Purpose
`intel_gt_print.h` provides GT-scoped logging and warning macros that prefix messages with the GT id.

### Important APIs, Types, And Functions
It defines `gt_err()`, `gt_warn()`, `gt_warn_once()`, `gt_notice()`, `gt_info()`, `gt_dbg()`, rate-limited error/notice helpers, `gt_probe_error()`, `gt_WARN()`, `gt_WARN_ONCE()`, `gt_WARN_ON()`, and `gt_WARN_ON_ONCE()`.

### Control Flow
Macros expand to DRM or device logging helpers using `(_gt)->i915->drm` and `(_gt)->info.id`. Warning macros feed the GT id into DRM warning output.

### State, Persistence, And Dependencies
No state is stored. Dependencies are DRM print helpers, GT types, and i915 utility macros.

### Integration Points
Used throughout GT code for diagnostics in probe, PM, MCR, faults, and error paths.

### Risks
Macros evaluate `_gt` for message context; callers must pass a valid GT pointer. Logging level and rate limiting affect support visibility.

### Test Signals
Compile coverage and dmesg/debug output that includes the expected `GT%u` prefix validate the macros.
