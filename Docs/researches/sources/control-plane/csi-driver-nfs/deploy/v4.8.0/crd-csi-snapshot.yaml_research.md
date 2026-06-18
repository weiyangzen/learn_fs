<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.8.0/crd-csi-snapshot.yaml

## Purpose
Installs the CSI snapshot API CRDs required by the snapshot-controller and CSI snapshotter sidecars. It defines the Kubernetes API surface for `VolumeSnapshot`, `VolumeSnapshotContent`, and `VolumeSnapshotClass` in group `snapshot.storage.k8s.io`.

## Important APIs, Types, and Functions
The file contains `apiextensions.k8s.io/v1` `CustomResourceDefinition` objects with generated OpenAPI v3 schemas, printer columns, `status` subresources, and version blocks. `VolumeSnapshot` is namespaced and models user snapshot requests from a PVC or pre-existing content. `VolumeSnapshotContent` is cluster-scoped and models the physical snapshot handle, driver, source, deletion policy, class, reference, and status. `VolumeSnapshotClass` is cluster-scoped and carries driver parameters and deletion policy.

## Control Flow, State, and Persistence
The API server persists snapshot desired state and status. The v1 versions are served and storage versions; v1beta1 versions are present for compatibility and deprecation warnings, with some v1beta1 content marked unserved/non-storage. Snapshot controllers update status subresources, while users and sidecars create spec objects according to the schema's immutability and required-field constraints.

## Dependencies and Integration Points
The CRDs are consumed by `snapshot-controller`, `csi-snapshotter`, storage provisioners, and applications that restore PVCs from snapshots. They encode CSI fields such as snapshot handles, volume handles, restore size, ready-to-use state, deletion policy, and driver names.

## Risks and Test Signals
Risks include CRD version skew with snapshot-controller v8 sidecars, stale v1beta1 clients, missing status subresource permissions, and schema validation rejecting older manifests. Signals are successful CRD establishment, discovery of `snapshot.storage.k8s.io/v1`, snapshot-controller readiness, accepted `VolumeSnapshotClass` objects, and status updates on created snapshots.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/crd-csi-snapshot.yaml -->
