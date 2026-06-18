<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_control.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_control.h

Purpose: declares PF VF-control operations used by debugfs/sysfs/service callers.

Important APIs: pause, resume, stop, reset, prepare/wait/sync FLR, trigger/finish save, and trigger/finish restore for a VF ID.

Risks and test signals: callers must pass a valid nonzero VF ID where required. Tests should exercise APIs through debugfs wrappers and direct service paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_control.h -->
