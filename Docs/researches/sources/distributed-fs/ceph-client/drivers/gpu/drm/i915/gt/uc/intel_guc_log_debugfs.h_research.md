## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_log_debugfs.h

Purpose: declares the GuC log debugfs registration function.

Important APIs, types, and functions:
- Forward declares `struct intel_guc_log` and `struct dentry`.
- Exposes `intel_guc_log_debugfs_register(struct intel_guc_log *log, struct dentry *root)`.

Control flow:
- GuC debugfs setup calls this helper after registering general GuC files.

State and persistence:
- No owned state; implementation creates debugfs entries tied to the provided root and log object.

Dependencies and integration points:
- Connects `intel_guc_debugfs.c` to log-specific dump, level, and relay controls.

Risks:
- Minimal header risk; runtime availability is enforced in the implementation.

Test signals:
- Build coverage and debugfs registration checks for GuC log files.
