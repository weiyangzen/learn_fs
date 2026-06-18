<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf.c

Purpose: implements PF readiness, early/late PF initialization, readiness waiting, exclusive/lockdown guards, VF enable lockdown, and VF summary printing.

Important APIs and control flow: `xe_sriov_pf_readiness()` verifies PCI PF, GuC submission, configured maximum VFs, reduces total VFs to driver limit, and records admin-only/device/driver VF counts. `xe_sriov_pf_init_early()` allocates per-VF state for VF0..N, initializes the master mutex, migration state, VFs-enabling guard, PF service, and MERT. `xe_sriov_pf_init_late()` initializes each GT PF side and PF sysfs. Guard wrappers add SR-IOV debug logging around `xe_guard_arm()`/`xe_guard_disarm()`.

State and dependencies: PF state includes `admin_only`, `device_total_vfs`, `driver_max_vfs`, `vfs[]`, `master_lock`, service state, migration state, and guard. Depends on configfs policy, PCI total VF APIs, GT PF modules, service/sysfs/provisioning, MERT, and DRM managed allocation.

Risks and test signals: when prerequisites fail, PF mode intentionally continues as native and sets total VFs to zero. Tests should cover configfs max VF reduction, admin-only propagation, guard denial while VFs are enabled, wedged-device readiness failure, and late init failure propagation across GTs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf.c -->
