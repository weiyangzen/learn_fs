# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_policy.c

Purpose: manages PF GT SR-IOV GuC policies, including scheduling-if-idle, reset-after-VF-switch, adverse event sample period, and scheduler group mode provisioning.

Important APIs and functions: public setters/getters for `sched_if_idle`, `reset_engine`, `sample_period`, scheduler group support/mode/enabled checks, `xe_gt_sriov_pf_policy_init`, `sanitize`, `reprovision`, and `print`. Internal helpers build GuC KLV payloads and send `GUC_ACTION_PF2GUC_UPDATE_VGT_POLICY`.

Control flow: setters take the PF master mutex, push a KLV to GuC, and update cached policy only on success. Reprovision optionally resets cached policy to defaults, then pushes all policy KLVs with runtime PM held. Scheduler group init computes supported media-slice grouping modes from hardware engines and GuC/platform capability. Scheduler group mode changes are rejected if VFs are active or MLRC queues are registered.

State and persistence: cached policy lives in `gt->sriov.pf.policy.guc`. Scheduler group mode data stores max group count, supported mode mask, current mode, and per-mode group arrays allocated with DRM managed memory.

Dependencies and integration: depends on GuC KLV helpers/ABI, GuC CT/buffer APIs, hardware engine iteration, runtime PM, GuC submit MLRC state, PF master mutex, and debugfs/provisioning callers.

Risks: `err |= ...` in reprovision compresses multiple failures into `-ENXIO`, which loses detail. Scheduler group support is hardcoded to max two groups pending firmware query support. Media-slice grouping is intentionally disabled for post-Battlemage platforms. Policy setters update cached state only after firmware success, so reset/sanitize/reprovision ordering matters.

Test signals: KLV count mismatch handling, firmware rejection paths, debugfs writes, reprovision after GT reset, scheduler group mode switching before/after enabling VFs, active MLRC rejection, and media GT grouping on BMG-class devices.
