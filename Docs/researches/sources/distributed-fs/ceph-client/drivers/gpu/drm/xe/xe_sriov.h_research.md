<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov.h

Purpose: declares top-level SR-IOV APIs and inline mode predicates.

Important APIs: `xe_sriov_mode_to_string()`, `xe_sriov_function_name()`, `xe_sriov_probe_early()`, `xe_sriov_print_info()`, `xe_sriov_init()`, and `xe_sriov_init_late()`. Inlines expose `xe_device_sriov_mode()`, `xe_device_is_sriov_pf()`, `xe_device_is_sriov_vf()`, and macros `IS_SRIOV_PF`, `IS_SRIOV_VF`, and `IS_SRIOV`.

Risks and test signals: `xe_device_sriov_mode()` asserts mode was initialized, so it must not be called before early probe. PF predicate depends on `CONFIG_PCI_IOV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov.h -->
