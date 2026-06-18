<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov.c

Purpose: provides top-level SR-IOV mode detection, common initialization, workqueue lifetime, info printing, function-name formatting, and late init dispatch for PF or VF mode.

Important APIs and control flow: `xe_sriov_probe_early()` determines mode from device capability, VF MMIO register `VF_CAP_REG`, and PF readiness, or disables advertised VFs when platform SR-IOV support is not enabled. `xe_sriov_init()` calls PF or VF early init as appropriate, creates `xe-sriov-wq`, and registers managed cleanup. `xe_sriov_init_late()` dispatches to PF or VF late init.

State and dependencies: sets `xe->sriov.__mode`, `xe->sriov.wq`, and PF/VF-specific state. Depends on PCI SR-IOV APIs, MMIO, PF and VF modules, DRM managed cleanup, and fault-injection annotation.

Risks and test signals: mode is asserted nonzero after probing, so probe ordering is critical. Tests should cover PF readiness false, VF detection via MMIO, unsupported platform with total VFs advertised, workqueue allocation failure, and function-name formatting for PF/VF IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov.c -->
