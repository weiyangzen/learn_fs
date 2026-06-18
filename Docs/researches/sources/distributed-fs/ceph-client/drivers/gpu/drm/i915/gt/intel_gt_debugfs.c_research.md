# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_debugfs.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_debugfs.c

### Purpose
`intel_gt_debugfs.c` creates the per-GT debugfs root and registers core GT debug controls, including reset injection/status and MCR steering reports.

### Important APIs, Types, And Functions
Public functions are `intel_gt_debugfs_register()`, `intel_gt_debugfs_register_files()`, `intel_gt_debugfs_reset_show()`, and `intel_gt_debugfs_reset_store()`. Internal files include `reset` and `steering`.

### Control Flow
Registration creates `gtN` under the DRM debugfs root, installs core files, then delegates to engine, PM, SSEU, and UC debugfs registration. The reset read maps terminal wedge status to 0/1, and reset write waits for reset backoff to clear before calling `intel_gt_handle_error()` with the user-provided engine mask. The steering file prints MCR steering state through a `drm_printer`.

### State, Persistence, And Dependencies
The file persists debugfs dentries through debugfs infrastructure and reads GT reset/MCR state. Dependencies include debugfs, DRM printers, reset handling, MCR reporting, and submodule debugfs registration.

### Integration Points
Called from `intel_gt_driver_register()`. It is the parent registration point for GT engine, PM, SSEU, and UC diagnostics.

### Risks
Reset writes are a privileged debug interface and can disrupt active work. Registration silently skips when debugfs is absent. File registration relies on optional `eval()` callbacks to avoid exposing invalid files.

### Test Signals
Debugfs presence, per-GT directory creation on multi-GT systems, manual reset triggering, steering output on MCR platforms, and conditional file visibility are useful signals.
