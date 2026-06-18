<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_helpers.h

Purpose: provides PF-only inline helpers and guard declarations for VF count, admin-only policy, master mutex access, and VF ID assertions.

Important APIs: `xe_sriov_pf_assert_vfid()` validates VF IDs in debug builds; `xe_sriov_pf_get_totalvfs()` returns driver-supported VFs; `xe_sriov_pf_num_vfs()` returns currently enabled VFs via PCI; `xe_sriov_pf_admin_only()` exposes configfs policy; `xe_sriov_pf_master_mutex()` returns the PF master lock; guard arm/disarm declarations are implemented in `xe_sriov_pf.c`.

Risks and test signals: helpers assert PF mode, so calling them in native/VF mode is a bug. Tests should cover VF0/PFID allowance where documented and nonzero VF requirements in higher-level callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_helpers.h -->
