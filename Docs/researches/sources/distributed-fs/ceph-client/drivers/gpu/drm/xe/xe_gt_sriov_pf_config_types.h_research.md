# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_config_types.h

## Purpose
Defines persistent configuration data structures used by the SR-IOV PF provisioning module.

## Important Types and Fields
- `struct xe_gt_sriov_config` stores per-PF/VF assigned resources: GGTT node, LMEM BO, GuC context range, doorbell range, per-scheduler-group execution quantum and preempt timeout, scheduler priority, and GuC threshold values.
- `struct xe_gt_sriov_spare_config` stores PF spare reservations for GGTT, LMEM, context IDs, and doorbells that constrain fair/available provisioning.

## State and Persistence
Instances live under `gt->sriov.pf.vfs[]` for PF/VF config and `gt->sriov.pf.spare` for spare config. Pointers reference resources owned elsewhere (`xe_ggtt_node`, `xe_bo`) and must be released by config teardown.

## Dependencies and Integration
Depends on GuC scheduler ABI group count, GGTT node type, and GuC KLV threshold count. The structures are mutated under the PF master mutex by `xe_gt_sriov_pf_config.c`.

## Risks and Test Signals
- Array sizes are ABI-coupled to GuC scheduler groups and threshold enumerations; KLV encoding has build-time checks for group lengths.
- Tests should verify zero-initialized config means no assigned VF resources except PF self config prepared at init.
