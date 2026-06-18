# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_debugfs.c

Purpose: Registers the debugfs subtree for Xe microcontroller diagnostics.

Important APIs/types/functions: Public function `xe_uc_debugfs_register(struct xe_uc *uc, struct dentry *parent)` creates a `uc` debugfs directory and delegates registration to GSC, GuC, and HuC debugfs helpers.

Control flow: Debugfs setup calls this with the parent GT/device debugfs dentry. The function creates `uc`; if creation fails, it warns and returns. Otherwise it calls `xe_gsc_debugfs_register`, `xe_guc_debugfs_register`, and `xe_huc_debugfs_register`.

State and persistence behavior: Persists debugfs dentries/files until debugfs teardown. Does not mutate firmware state, only exposes diagnostics/control surfaces supplied by child subsystems.

Dependencies and integration points: Depends on Linux debugfs, DRM debugfs, Xe GSC/GuC/HuC debugfs helpers, macros, and `xe_uc_types.h`.

Risks: `debugfs_create_dir` failures are non-fatal. Child registration assumes `uc` substructures are initialized enough for their debugfs callbacks. Debugfs callbacks may need PM/runtime locking in child code.

Test signals: Mount debugfs and verify `uc` directory plus GSC/GuC/HuC entries appear for a GT. Inject debugfs creation failure or run with debugfs disabled to confirm graceful behavior.
