## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_debugfs.h

Purpose: declares the GuC debugfs registration entry point.

Important APIs, types, and functions:
- Forward declares `struct intel_guc` and `struct dentry`.
- Exposes `intel_guc_debugfs_register(struct intel_guc *guc, struct dentry *root)`.

Control flow:
- GT/debugfs setup calls this function with the GuC instance and root dentry. The implementation decides which files to register based on GuC support and feature use.

State and persistence:
- No owned state; debugfs dentries are created by the implementation and tied to the parent root.

Dependencies and integration points:
- Integrates the GuC-specific debugfs file table into the broader GT debugfs hierarchy.

Risks:
- Minimal header risk; the main risk is keeping declaration and implementation signatures synchronized.

Test signals:
- Build coverage and runtime verification that GuC debugfs files appear under the GT debugfs root.
