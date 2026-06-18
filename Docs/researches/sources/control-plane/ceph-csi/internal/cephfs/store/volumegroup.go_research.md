## sources/control-plane/ceph-csi/internal/cephfs/store/volumegroup.go

Purpose: Provides store-layer option parsing and journal operations for CephFS volume group snapshots.

Important types/functions: `VolumeGroupOptions`, `NewVolumeGroupOptions`, `VolumeGroupSnapshotIdentifier`, `GetVolumeIDs`, `NewVolumeGroupOptionsFromID`, `CheckVolumeGroupSnapExists`, `ReserveVolumeGroup`, and `UndoVolumeGroupReservation`.

Control flow: Create path parses request parameters into volume options, extracts optional `volumeGroupNamePrefix`, connects to Ceph, resolves filesystem ID and metadata pool, and reserves/checks group snapshot names through `VolumeGroupJournal`. ID lookup decomposes the CSI group snapshot ID, resolves monitors/RADOS namespace from config, connects, resolves filesystem name and metadata pool, loads group attributes from the journal, and returns the volume-to-snapshot map.

State and persistence: Persists group snapshot reservation and `VolumeSnapshotMap` in RADOS OMAP via `VolumeGroupJournal`. Generated CSI IDs encode cluster ID, filesystem location ID, and group UUID.

Dependencies and risks: Depends on CSI group snapshot request types, `VolumeOptions` parsing, core filesystem lookup, util CSI ID/config helpers, and group journal implementation. Missing journal group name maps to `ErrGroupNotFound`. Tests in this subset do not exercise this store code directly; integration should validate ID decode failures, missing config, group map retrieval, reservation idempotency, and undo behavior.
