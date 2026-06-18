# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_monitor_types.h

Purpose: defines per-VF PF monitoring storage for GuC adverse events.

Important type: `struct xe_gt_sriov_monitor` contains `guc.events[XE_GUC_KLV_NUM_THRESHOLDS]`, one counter per configured GuC threshold.

Control flow: event indexes come from `xe_guc_klv_threshold_key_to_index`; debug printing uses the same threshold set macro to name fields.

State and persistence: counters are volatile per-VF state, reset by FLR and initialized with VF metadata allocation.

Dependencies and integration: includes `xe_guc_klv_thresholds_set_types.h`; embedded in `xe_gt_sriov_pf_types.h`.

Risks: threshold set macro changes must keep the array size and printer mappings consistent.

Test signals: compile with new threshold definitions and verify array bounds with all generated threshold attributes/events.
