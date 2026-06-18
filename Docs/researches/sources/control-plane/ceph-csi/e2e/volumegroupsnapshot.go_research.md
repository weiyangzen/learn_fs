# sources/control-plane/ceph-csi/e2e/volumegroupsnapshot.go

Purpose: driver-specific VolumeGroupSnapshot e2e implementations for CephFS and RBD, layered over the shared base workflow.

Important APIs and flow: `newCephFSVolumeGroupSnapshot` and `newRBDVolumeGroupSnapshot` create a `volumeGroupSnapshotterBase` and wrap it with driver-specific validation. Both `TestVolumeGroupSnapshot` methods delegate to the base. CephFS `GetVolumeGroupSnapshotClass` loads the CephFS group snapshot class, injects secret refs, `fsName`, and cluster ID. CephFS create validation obtains the metadata pool, inspects the `VolumeGroupSnapshotContent`, computes expected derived `VolumeSnapshot` names from group snapshot UID plus volume handle, validates clone subvolume count, per-source snapshot count, and OMAP counts for volumes/snaps/groupsnaps. CephFS delete validation requires zero OMAP counts. RBD class setup injects RBD secret refs, pool, and cluster ID; create validation checks volume OMAP count after clones; delete validation checks zero volume/snap/group OMAPs, zero RBD images, and trash cleanup.

State and persistence: creates driver-specific `VolumeGroupSnapshotClass` parameters and validates backend CephFS metadata pool OMAPs, CephFS subvolume snapshots, RBD OMAPs, RBD images, and trash entries.

Dependencies and integration: depends on external-snapshotter group snapshot APIs, shared base workflow, cluster ID discovery, CephFS metadata pool helpers, OMAP validators, RBD image/trash helpers, and example group snapshot class YAML.

Risks and test signals: derived snapshot names duplicate external-snapshotter naming logic using SHA256 of UID and volume handle, so upstream naming changes would break validation. Backend count assertions are strong but can fail if unrelated test resources share the same pools. Passing tests signal that group snapshots create per-volume snapshots, clones can be created, and driver metadata is fully cleaned.
