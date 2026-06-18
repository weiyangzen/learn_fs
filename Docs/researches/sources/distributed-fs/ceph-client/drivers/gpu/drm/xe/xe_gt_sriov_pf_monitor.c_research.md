# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_monitor.c

Purpose: tracks PF-side adverse threshold events reported by GuC for PF/VF functions and resets per-VF counters on FLR.

Important APIs and functions: `xe_gt_sriov_pf_monitor_flr`, `xe_gt_sriov_pf_monitor_process_guc2pf`, and `xe_gt_sriov_pf_monitor_print_events`. Internal helpers map threshold KLV keys to indexes and increment `monitor.guc.events`.

Control flow: GuC adverse event messages are validated for origin/type/action, MBZ fields, length, VFID range, and threshold key. Valid events increment the corresponding counter and log threshold exceedance with the configured threshold value. FLR zeroes all counters for the VF.

State and persistence: per-VF counters live in `gt->sriov.pf.vfs[vfid].monitor.guc.events`; they are volatile and reset on FLR or driver unload.

Dependencies and integration: depends on GuC message ABI, KLV threshold helpers, PF config threshold getters, PF helpers, and SR-IOV logging. Debugfs exposes counters through `adverse_events`.

Risks: unknown threshold keys return `-ENOTCONN`, which may indicate ABI drift. Counters are plain integers and not protected by a lock; event dispatch serialization is assumed by the GuC event handling path.

Test signals: inject/observe GuC adverse events for every threshold, verify debugfs output hides empty VFs unless debug SR-IOV is enabled, test invalid MBZ/length/VFID/key handling, and confirm FLR clears counters.
