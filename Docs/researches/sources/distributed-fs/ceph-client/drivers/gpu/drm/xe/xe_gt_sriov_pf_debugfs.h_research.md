# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_debugfs.h

Purpose: declares PF-specific GT SR-IOV debugfs registration and population entry points.

Important APIs: `xe_gt_sriov_pf_debugfs_register` adds symlinks from GT debugfs to the SR-IOV tree, and `xe_gt_sriov_pf_debugfs_populate` creates per-GT directories under PF/VF SR-IOV debugfs branches. When `CONFIG_PCI_IOV` is disabled, `register` becomes a no-op; no no-op is provided for `populate`.

Control flow: the header separates ordinary GT debugfs registration from SR-IOV hierarchy population.

State and persistence: no state is stored here; debugfs dentry private data and PF structures are managed in the implementation.

Dependencies and integration: forward-declares `struct xe_gt` and `struct dentry`; included by debugfs setup code.

Risks: callers must be gated correctly under PCI IOV for `populate`, since only `register` has a stub. Incorrect parent dentry layout will break implementation asserts.

Test signals: build with `CONFIG_PCI_IOV` enabled and disabled, and verify no unresolved references for debugfs setup paths.
