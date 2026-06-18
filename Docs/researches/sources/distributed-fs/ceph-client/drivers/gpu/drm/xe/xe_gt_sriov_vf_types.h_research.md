# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_vf_types.h

Purpose: defines GT-level VF SR-IOV state structures.

Important types: `xe_gt_sriov_vf_selfconfig` stores assigned GuC contexts and doorbells. `xe_gt_sriov_vf_runtime` stores GMDID, scheduler group flag, and PF-provided runtime register offset/value array. `xe_gt_sriov_vf_migration` stores recovery worker, lock, waitqueue, scratch buffer, fixup counter, debug stoppers, resfix marker, and recovery/ggtt flags. `xe_gt_sriov_vf` aggregates negotiated GuC versions, self config, runtime, and migration.

Control flow: config/runtime queries fill self_config/runtime; migration event handling drives migration fields and waitqueue; debugfs can set `debug.resfix_stoppers`.

State and persistence: all fields are volatile driver state, allocated/initialized during VF GT setup and torn down with device-managed actions.

Dependencies and integration: includes Linux types/wait/workqueue and Xe firmware version types; embedded in main GT SR-IOV union/state.

Risks: booleans used with `READ_ONCE`/`WRITE_ONCE` and barriers in implementation must remain aligned with waitqueue semantics. Runtime register array size/count separation must be respected when resizing.

Test signals: migration recovery state transitions, runtime register resize, fixup count waits, and debug stopper behavior.
