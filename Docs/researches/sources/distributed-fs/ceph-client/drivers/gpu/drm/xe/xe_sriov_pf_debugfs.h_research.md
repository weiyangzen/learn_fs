<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_debugfs.h

Purpose: declares PF SR-IOV debugfs registration with a stub for non-PCI_IOV builds.

Important API: `xe_sriov_pf_debugfs_register(struct xe_device *xe, struct dentry *root)` populates the PF debugfs tree when SR-IOV PF support is compiled in.

Risks and test signals: compile coverage should include PCI_IOV disabled builds to confirm the stub is used and no debugfs references leak.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_debugfs.h -->
