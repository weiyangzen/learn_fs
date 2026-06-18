# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_policy.h

Purpose: declares the PF GT SR-IOV policy API and scheduler group mode helpers.

Important APIs: policy setters/getters for scheduler-if-idle, reset-engine, sample period; scheduler group support, mode support, mode set, and enabled checks; init/sanitize/reprovision/print.

Control flow: callers use setters for live updates, `sanitize` to reset cached policy, and `reprovision` after reset or when pushing cached/default values to GuC.

State and persistence: no state in the header; state is in `struct xe_gt_sriov_pf_policy` from the types header.

Dependencies and integration: includes `xe_gt_sriov_pf_policy_types.h`; used by PF debugfs, provisioning, and PF GT init/reset flows.

Risks: callers must hold no conflicting locks before setters because implementation takes the PF master mutex and runtime PM in reprovision.

Test signals: compile API coverage and lockdep during debugfs/provisioning updates.
