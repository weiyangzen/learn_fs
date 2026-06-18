<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf.h

Purpose: declares PF-specific SR-IOV lifecycle and reporting APIs, with no-op stubs when `CONFIG_PCI_IOV` is disabled.

Important APIs: PF readiness, early/late init, wait-ready, lockdown/end-lockdown, and VF summary printing. The disabled-config stubs keep non-IOV builds compiling.

Risks and test signals: callers should not assume `xe_sriov_pf_wait_ready()` has a stub in every disabled path unless build coverage confirms it. Tests should compile both PCI_IOV enabled and disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf.h -->
