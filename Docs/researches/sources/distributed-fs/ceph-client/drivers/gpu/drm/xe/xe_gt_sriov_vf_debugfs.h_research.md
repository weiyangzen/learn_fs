# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_vf_debugfs.h

Purpose: declares VF GT debugfs registration.

Important API: `xe_gt_sriov_vf_debugfs_register(struct xe_gt *gt, struct dentry *root)`.

Control flow: GT debugfs setup calls this for VF devices to add the `vf` subtree.

State and persistence: no state in the header.

Dependencies and integration: forward-declares GT and dentry types; implemented unconditionally with VF assertions.

Risks: no compile-time stub is provided, so build integration must avoid calling it in non-debugfs contexts only if the rest of debugfs code is absent.

Test signals: compile and VF debugfs registration smoke tests.
