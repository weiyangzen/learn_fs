# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_debugfs.h

Purpose: Declares uC debugfs registration.

Important APIs/types/functions: Forward declares `struct dentry` and `struct xe_uc`, and declares `xe_uc_debugfs_register`.

Control flow: Debugfs setup code uses this to attach the uC diagnostics subtree under a parent dentry.

State and persistence behavior: No state in the header.

Dependencies and integration points: Included by higher-level debugfs setup code and implemented by `xe_uc_debugfs.c`.

Risks: Minimal. Callers must pass a valid parent dentry and initialized `xe_uc`.

Test signals: Build coverage and presence of the `uc` debugfs directory at runtime.
