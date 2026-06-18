# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/groupsnapshotclass.yaml

Purpose: optionally renders a `VolumeGroupSnapshotClass` for RBD group snapshots.

Important APIs/types/functions: gated by `.Values.volumeGroupSnapshotClass.create`; emits `groupsnapshot.storage.k8s.io/v1beta2`, driver name, `clusterID`, `pool`, optional `volumeGroupNamePrefix`, group snapshotter secret name/namespace, annotations, labels, and deletion policy.

Control flow: when enabled, the external snapshotter group-snapshot feature can use this class to create group snapshot content through the RBD CSI driver.

State and persistence behavior: cluster-scoped snapshot class state; actual group snapshots are separate CRs and Ceph RBD group resources.

Dependencies and integration points: requires group snapshot CRDs/controllers and matching provisioner RBAC/sidecar feature gate.

Risks: API is beta; missing CRDs or disabled sidecar feature gates make this object unusable. `clusterID` and `pool` must match configured Ceph cluster/pool.

Test signals: group snapshot e2e coverage and Helm rendering with the create flag enabled.
