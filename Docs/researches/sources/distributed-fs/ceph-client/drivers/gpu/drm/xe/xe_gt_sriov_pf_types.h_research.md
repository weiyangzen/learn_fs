# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_types.h

Purpose: aggregates all GT-level PF SR-IOV state into metadata structures embedded in `struct xe_gt`.

Important types: `struct xe_gt_sriov_metadata` stores per-VF config, monitor, control, negotiated VF/PF version, and migration data. `struct xe_gt_sriov_pf_workers` currently stores the restart worker. `struct xe_gt_sriov_pf` stores workers, service, control, policy, spare PF config, and an array of per-VF metadata.

Control flow: per-VF metadata is indexed by VFID, with VFID 0 representing PF in several paths. Control code relies on pointer arithmetic from `control` back to the metadata array to recover VFID.

State and persistence: all fields are in-memory driver state, initialized by PF GT setup and reset/sanitized by lifecycle paths. `vfs` is the core per-VF backing store.

Dependencies and integration: includes PF config, control, migration, monitor, policy, and service type headers.

Risks: layout coupling matters because `container_of(... control)` and array index math assume every `control` belongs to `gt->sriov.pf.vfs`. Any allocation/count bug in `vfs` affects all PF subsystems.

Test signals: PF init allocation for total VFs plus PFID, VFID indexing assertions, restart worker teardown, and migration/control operations over first/last VFIDs.
