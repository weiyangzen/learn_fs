# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc_debugfs.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc_debugfs.c

### Purpose
`intel_gsc_uc_debugfs.c` exposes GSC firmware and FWSTS status through GT debugfs.

### Important APIs, Types, And Functions
It defines `gsc_info_show()`, `DEFINE_INTEL_GT_DEBUGFS_ATTRIBUTE(gsc_info)`, and `intel_gsc_uc_debugfs_register()`.

### Control Flow
The show callback rejects unsupported GSC with `-ENODEV`, creates a `drm_printer` for the seq file, and delegates to `intel_gsc_uc_load_status()`. Registration adds a `gsc_info` debugfs file only when GSC is supported.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
State is just debugfs file registration with the private `intel_gsc_uc` pointer. Dependencies include DRM print, GT debugfs helpers, and GSC status printing. Integration is user-facing diagnostics. Risks are exposing unsupported devices or reading status without runtime PM, handled by the delegated printer. Test signals are presence/absence of `gsc_info` and meaningful firmware/FWSTS output.
