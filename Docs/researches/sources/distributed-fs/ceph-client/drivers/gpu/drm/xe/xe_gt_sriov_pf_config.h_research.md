# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_config.h

## Purpose
Declares the SR-IOV PF provisioning API for per-VF resources, scheduling controls, thresholds, save/restore, lifecycle, and diagnostics.

## Important APIs
- Resource provisioning: GGTT, contexts, doorbells, and LMEM each expose get/set, fair, and bulk functions, with LMEM additionally exposing locked variants and BO reference acquisition.
- Scheduling: execution quantum and preemption timeout expose scalar, locked, bulk-locked, and scheduler-group APIs; scheduler priority has get/set.
- Thresholds: generic get/set by `enum xe_guc_klv_threshold_index`.
- Operations: `set_fair`, `sanitize`, `release`, `push`, `save`, `restore`, GGTT save/restore, `is_empty`, `init`, and `restart`.
- Diagnostics: print functions for GGTT, contexts, doorbells, LMEM, and available GGTT.

## Integration and Risks
This header is the contract used by PF provisioning, debugfs, migration, and control modules. Locked APIs require the PF master mutex to already be held; misuse can deadlock or trip lockdep assertions. Callers must distinguish PFID (`0`) spare/self configuration from VFIDs (`1..n`).
