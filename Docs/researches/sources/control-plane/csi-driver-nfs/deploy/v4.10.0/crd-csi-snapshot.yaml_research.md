# sources/control-plane/csi-driver-nfs/deploy/v4.10.0/crd-csi-snapshot.yaml

Purpose: installs the CSI snapshot API CRDs used by the NFS driver snapshot examples and by the snapshot sidecars. It defines `VolumeSnapshot` as a namespaced resource and `VolumeSnapshotClass` plus `VolumeSnapshotContent` as cluster-scoped resources under `snapshot.storage.k8s.io/v1`.

Important APIs/types/functions: the three `CustomResourceDefinition` objects expose the Kubernetes snapshot types, OpenAPI schemas, status subresources, additional printer columns, and accepted spec/status fields. Key fields include `VolumeSnapshot.spec.source`, `volumeSnapshotClassName`, `status.readyToUse`, `status.restoreSize`, `VolumeSnapshotClass.driver`, `deletionPolicy`, `parameters`, and `VolumeSnapshotContent.spec.source` with either `volumeHandle` or `snapshotHandle`.

Control flow: this manifest has no executable code; applying it extends the apiserver before `csi-snapshot-controller`, `csi-snapshotter`, `VolumeSnapshotClass`, and `VolumeSnapshot` objects are created. Snapshot creation then flows from a `VolumeSnapshot` to the external snapshot controller, through `VolumeSnapshotContent`, and finally through the NFS CSI driver's snapshot RPCs.

State and persistence: the CRDs make snapshot objects durable Kubernetes API state. `VolumeSnapshotContent` records binding, driver identity, deletion policy, source handles, ready state, restore size, and error status; actual NFS data remains in the driver/backend rather than in the CRD itself.

Dependencies and integration points: depends on Kubernetes `apiextensions.k8s.io/v1` and a cluster version supporting `snapshot.storage.k8s.io/v1`. It integrates with `rbac-snapshot-controller.yaml`, `csi-snapshot-controller.yaml`, `snapshotclass.yaml`, and the NFS controller's `csi-snapshotter` sidecar.

Risks: CRDs must be installed before snapshot controller pods become ready. Removing this file during uninstall can delete all snapshot API objects and their status history. Schema drift from the external-snapshotter version can break admission or controller expectations, and cluster-scoped snapshot content objects need careful RBAC.

Test signals: useful checks are `kubectl apply --server-side --dry-run=server`, `kubectl get crd volumesnapshots.snapshot.storage.k8s.io`, creating `snapshotclass.yaml`, creating `example/snapshot/snapshot-nfs-dynamic.yaml`, and restoring with `pvc-nfs-snapshot-restored.yaml`.
