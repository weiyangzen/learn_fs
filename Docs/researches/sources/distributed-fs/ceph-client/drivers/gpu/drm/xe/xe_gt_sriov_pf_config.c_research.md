# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_config.c

## Purpose
Owns per-GT SR-IOV PF provisioning state and pushes VF/PF configuration to GuC as KLVs. It provisions GGTT, LMEM/VRAM, GuC context IDs, doorbells, execution quantum, preemption timeout, scheduler priority, adverse-event thresholds, save/restore blobs, sanitization, and debug printouts.

## Important APIs and Functions
- Resource getters/setters: `xe_gt_sriov_pf_config_get/set/bulk/fair_ggtt`, `_ctxs`, `_dbs`, and `_lmem`.
- Scheduling controls: `xe_gt_sriov_pf_config_get/set_exec_quantum`, locked/bulk variants, group execution quantum APIs, preempt timeout APIs, group preempt timeout APIs, and scheduler priority APIs.
- Threshold controls: `xe_gt_sriov_pf_config_get_threshold` and `xe_gt_sriov_pf_config_set_threshold`.
- Lifecycle and operations: `xe_gt_sriov_pf_config_init`, `xe_gt_sriov_pf_config_restart`, `xe_gt_sriov_pf_config_release`, `xe_gt_sriov_pf_config_sanitize`, `xe_gt_sriov_pf_config_push`, `xe_gt_sriov_pf_config_is_empty`, `xe_gt_sriov_pf_config_save`, and `xe_gt_sriov_pf_config_restore`.
- Migration/data helpers: `xe_gt_sriov_pf_config_ggtt_save`, `xe_gt_sriov_pf_config_ggtt_restore`, and `xe_gt_sriov_pf_config_get_lmem_obj`.
- Debug printers: config print functions for GGTT, contexts, doorbells, LMEM, and available GGTT.

## Control Flow
- GuC updates flow through `guc_action_update_vf_cfg`, `pf_send_vf_cfg_reset`, and KLV push helpers. Push replies must equal the number of KLVs sent or the code reports `-ENOKEY`/`-EPROTO`.
- Configuration is selected with `pf_pick_vf_config` under `xe_gt_sriov_pf_master_mutex(gt)`.
- Full config encoding writes KLVs for GGTT, contexts, doorbells, LMEM, scheduling, and thresholds; media GT config borrows GGTT from the primary GT, while PF self config fakes full GGTT coverage.
- Provisioning a resource generally clears old GuC config to zero, releases local resource, refreshes full config, allocates/reserves new resource, pushes new KLVs, and rolls back on failure.
- Fair provisioning estimates available resources after PF spare reservations, clamps to platform/profile limits, and bulk provisions a VF range.
- Restart pushes PF self config, skips empty VFs, and repushes all non-empty VF configs after GT reset because GuC lost previous KLV state.
- Restore parses a saved KLV stream, resets GuC/local config first, then provisions each recognized key and validates mandatory configuration.

## State and Persistence
- Persistent per-function data is in `gt->sriov.pf.vfs[vfid].config`; PF spare reservations are in `gt->sriov.pf.spare`.
- GGTT state is represented by assigned `xe_ggtt_node`s; LMEM state by pinned VRAM BOs and optional LMTT page tables across tiles; contexts and doorbells are ranges reserved in GuC managers.
- Execution quantum/preempt timeout arrays hold per scheduler group values; scalar APIs replicate one value across all groups. Thresholds are stored by `xe_guc_klv_threshold_index`.
- Devm cleanup releases all VF configs at driver teardown.

## Dependencies and Integration Points
Depends on GuC CT, GuC KLV ABI/helpers, GuC ID and doorbell managers, GGTT, LMEM/TTM VRAM manager, LMTT, migration clear, WOPCM/GGTT ranges, SR-IOV PF policy/provision/debugfs/migration/control code, and GT logging.
- Provisioning APIs are called by `xe_sriov_pf_provision.c`.
- Print and config blob APIs are consumed by SR-IOV PF debugfs.
- GGTT/LMEM object save/restore is used by SR-IOV migration.
- Sanitization is called by PF control when resetting or preparing VFs.

## Risks and Edge Cases
- All mutation assumes the PF master mutex is held; locked APIs assert this and unlocked APIs take the mutex internally.
- Some release paths call `pf_release_vf_config_ggtt` without null checks; current callers are expected to only release configured nodes or rely on lower helpers tolerating null if they do.
- Fair resource profiles contain preliminary hard-coded values and debug-build caps, so production provisioning should be validated against platform resource maps.
- LMEM provisioning requires LMTT support and DGFX; failures after BO allocation must reset LMTT and release pinned BOs.
- Restore rejects unsupported KLVs on media GT and thresholds unsupported by current GuC firmware.
- Partial bulk provisioning logs prior successes and the failed VF, but leaves already-provisioned VFs changed.

## Test Signals
- The file includes `tests/xe_gt_sriov_pf_config_kunit.c` when built for Xe KUnit, indicating direct unit coverage exists for provisioning logic.
- Integration tests should cover GuC KLV push counts, GGTT allocation/spare enforcement, LMEM/LMTT update across tiles, context/doorbell manager reservations, fair provisioning, config save/restore, reset restart repush, and forced release after GuC failure.
- Debugfs printouts for GGTT/ctxs/dbs/LMEM and provisioning sysfs/debugfs controls provide observable state for manual validation.
