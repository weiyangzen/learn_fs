# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_helpers.h

Purpose: provides GT-scoped convenience wrappers around device-level SR-IOV PF helper APIs.

Important APIs: `xe_gt_sriov_pf_assert_vfid`, `xe_gt_sriov_pf_get_totalvfs`, and `xe_gt_sriov_pf_master_mutex`.

Control flow: inline wrappers derive `struct xe_device` from `struct xe_gt` and forward to device-level helpers.

State and persistence: no stored state; it centralizes access to total VF count and the master PF mutex used to serialize provisioning/policy operations.

Dependencies and integration: includes `xe_gt_types.h` and `xe_sriov_pf_helpers.h`. Used broadly across PF control, config, policy, monitor, debugfs, and migration code.

Risks: wrappers assume the GT belongs to a PF-capable device. Locking correctness depends on callers consistently using the returned master mutex for shared PF state.

Test signals: compile-time inlining, debug assertions for invalid VFIDs, and lockdep coverage around PF policy/config updates.
