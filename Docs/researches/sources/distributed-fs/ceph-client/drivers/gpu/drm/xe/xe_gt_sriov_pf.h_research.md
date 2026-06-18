# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf.h

## Purpose
Declares the per-GT SR-IOV PF interface and provides no-op stubs when PCI IOV support is disabled.

## Important APIs
- Init/restart/readiness: `xe_gt_sriov_pf_init_early`, `xe_gt_sriov_pf_init`, `xe_gt_sriov_pf_init_hw`, `xe_gt_sriov_pf_restart`, and `xe_gt_sriov_pf_wait_ready`.
- Stop/sanitize: `xe_gt_sriov_pf_stop_prepare`, `xe_gt_sriov_pf_sanitize_hw`.
- Policy query: `xe_gt_sriov_pf_sched_groups_enabled`.

## Integration and Risks
When `CONFIG_PCI_IOV` is disabled most APIs become harmless stubs, but `xe_gt_sriov_pf_wait_ready` and `xe_gt_sriov_pf_sanitize_hw` are only declared in the enabled block. Callers must be guarded consistently by SR-IOV/PF configuration.
