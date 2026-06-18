<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_migration.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_migration.h

Purpose: declares PF migration lifecycle, capability, packet flow, waitqueue, size, and user-buffer streaming APIs.

Important APIs: migration init/supported/disable, restore produce, save consume, size query, waitqueue access, debugfs-facing read, and debugfs-facing write.

Risks and test signals: callers must pass PF devices and valid VF IDs. Tests should verify `xe_sriov_pf_migration_supported()` behavior in debug and non-debug builds after `xe_sriov_pf_migration_disable()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_migration.h -->
