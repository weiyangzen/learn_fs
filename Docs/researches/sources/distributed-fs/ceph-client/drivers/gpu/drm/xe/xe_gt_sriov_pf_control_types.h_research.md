# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_control_types.h

Purpose: defines PF-side GT SR-IOV control state bits and container structs used by `xe_gt_sriov_pf_control.c`.

Important types: `enum xe_gt_sriov_control_bits` enumerates WIP, FLR, pause, save, restore, resume, stop, terminal, failure, and mismatch bits. `struct xe_gt_sriov_control_state` stores the per-VF bitmap, completion, and queue link. `struct xe_gt_sriov_pf_control` stores the worker, pending list, and spinlock.

Control flow: the bit layout is the state-machine contract. `XE_GT_SRIOV_STATE_MISMATCH` must remain last because `XE_GT_SRIOV_NUM_STATES` is derived from it and controls bitmap sizing.

State and persistence: all state is in memory under `gt->sriov.pf.vfs[vfid].control` and `gt->sriov.pf.control`. Completion state is reinitialized per WIP operation; list membership is protected by the PF control spinlock.

Dependencies and integration: includes completion, spinlock, and workqueue type headers; embedded by `xe_gt_sriov_pf_types.h`.

Risks: adding states without updating debug string mapping or process ordering can create silent stuck states. Since state bits can coexist, callers must clear stale terminal/failure bits on successful transitions.

Test signals: build-time coverage for enum/string switch, debug logs that dump bitmaps, and stress tests for repeated queue/list movement under concurrent events.
