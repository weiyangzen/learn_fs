<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_debugfs.c

Purpose: builds the PF SR-IOV debugfs tree under the DRM minor root, exposing root PF controls, PF info, per-VF controls, migration data streams, migration size, and tile-level debugfs children.

Important APIs and control flow: `xe_sriov_pf_debugfs_register()` creates `sriov/`, `sriov/pf/`, and `sriov/vfN/` directories, storing either `xe_device *` or VF IDs in inode private data. Root files include `restore_auto_provisioning` and `lockdown_vfs_enabling`; PF files include `vfs` and `versions`; VF files include `pause`, `resume`, `stop`, `reset`, `save`, `restore`, `migration_data`, and `migration_size`. Boolean writes trigger runtime-PM-protected calls; save/restore use read-to-finish and write-to-trigger semantics.

State and dependencies: uses dentry parent relationships to derive `xe` and VF ID, runtime PM guards, PF control APIs, migration read/write/size, provisioning, service printing, and tile debugfs population.

Risks and test signals: debugfs is a privileged control surface. Tests should cover offset rejection for command writes and migration data, lockdown open/release balancing, VF ID extraction for PF versus VF dirs, partial migration reads/writes, and runtime PM ref balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_debugfs.c -->
