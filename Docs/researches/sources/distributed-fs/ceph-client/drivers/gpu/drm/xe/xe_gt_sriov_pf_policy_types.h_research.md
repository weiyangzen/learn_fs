# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_policy_types.h

Purpose: defines PF policy storage and scheduler group mode structures.

Important types: `enum xe_sriov_sched_group_modes` currently supports disabled and media-slices. `struct xe_gt_sriov_scheduler_groups` tracks max groups, supported mode mask, current mode, and per-mode `guc_sched_group` arrays. `struct xe_gt_sriov_guc_policies` stores boolean/u32 GuC policies plus scheduler groups. `struct xe_gt_sriov_pf_policy` wraps GuC policies.

Control flow: mode arrays are populated during policy init and consumed by provisioning and debugfs.

State and persistence: policy is volatile cached driver state mirrored to GuC by KLV updates; scheduler group arrays are DRM-managed allocations.

Dependencies and integration: includes GuC scheduler ABI for `GUC_MAX_ENGINE_CLASSES` and `struct guc_sched_group`.

Risks: adding enum modes requires updating mode string conversion, debugfs parser, init switch, and KLV provisioning behavior.

Test signals: compile with exhaustive enum switch warnings, debugfs mode listing, and KLV payload size validation for each mode.
