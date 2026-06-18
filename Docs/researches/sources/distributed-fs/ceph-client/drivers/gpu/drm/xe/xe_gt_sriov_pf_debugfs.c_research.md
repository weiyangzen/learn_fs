# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_debugfs.c

Purpose: builds the PF SR-IOV debugfs hierarchy for PF and VF GT views. It exposes provisioning, policy, scheduler group, thresholds, manual control, runtime registers, adverse events, and debug-only config blob access.

Important APIs and functions: public functions are `xe_gt_sriov_pf_debugfs_populate` and `xe_gt_sriov_pf_debugfs_register`. Helpers extract `xe_gt`, `xe_device`, and VFID from dentry private data. Macro-generated file operations handle policy (`reset_engine`, `sched_if_idle`, `sample_period_ms`), quotas/config (`contexts_quota`, `doorbells_quota`, `exec_quantum_ms`, `preempt_timeout_us`, `sched_priority`), thresholds, scheduler group arrays, and `control`.

Control flow: `xe_gt_sriov_pf_debugfs_populate` creates `gt%u` directories under PF/VF SR-IOV trees and delegates to `pf_populate_gt`. PF entries get policy/config/info files; VF entries get VF quota/config, `control`, scheduler group config, and optional `config_blob`. `xe_gt_sriov_pf_debugfs_register` creates symlinks in ordinary GT debugfs back to the SR-IOV tree.

State and persistence: debugfs itself is volatile. Writes mutate PF policy/config state through runtime PM guards, usually setting custom provisioning mode after successful changes. `config_blob_open` snapshots serialized config into heap memory per open; write restores a user-provided blob up to 4 KiB.

Dependencies and integration: depends on DRM debugfs helpers, PF config/provision APIs, PF policy, monitor, service runtime, PF control, runtime PM, and scheduler group GuC ABI constants.

Risks: debugfs is privileged but exposes powerful controls that can pause/stop VFs and overwrite config blobs. Dentry-parent assumptions are strict; hierarchy changes must update extraction helpers. Scheduler group debugfs is registered before policy init can fully determine valid groups, so some files may exist but return unsupported errors. Array parsing and count limits protect but need careful ABI testing.

Test signals: enumerate PF/VF debugfs tree, read info files, write all policy/quota/threshold attributes, verify custom provisioning mode transition, use `control` stop/pause/resume, test scheduler group mode with active VFs and active MLRC queues, and test config blob round trips in debug builds.
