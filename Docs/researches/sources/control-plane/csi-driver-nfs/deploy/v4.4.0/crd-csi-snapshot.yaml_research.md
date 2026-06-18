# sources/control-plane/csi-driver-nfs/deploy/v4.4.0/crd-csi-snapshot.yaml

## Purpose
This manifest installs the Kubernetes CSI snapshot API CRDs needed by the NFS CSI deployment. It defines `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` in the `snapshot.storage.k8s.io` API group, with both `v1` and `v1beta1` served versions and storage on `v1`.

## Important APIs, Types, and Functions
The important resources are three `apiextensions.k8s.io/v1` `CustomResourceDefinition` objects: `volumesnapshots.snapshot.storage.k8s.io`, `volumesnapshotclasses.snapshot.storage.k8s.io`, and `volumesnapshotcontents.snapshot.storage.k8s.io`. Their OpenAPI schemas define snapshot source selection, `volumeSnapshotClassName`, bound content references, CSI `driver`, `deletionPolicy`, `source.volumeHandle` or `source.snapshotHandle`, `restoreSize`, `readyToUse`, creation time, error status, and finalizer-preserving status subresources. Additional printer columns expose readiness, source PVC/content, driver, deletion policy, restore size, bound snapshot, namespace, and age.

## Control Flow, State, and Persistence
There is no executable control flow, but the CRDs create persistent cluster-scoped API storage. Snapshot lifecycle state is persisted in custom resources and status subresources: `VolumeSnapshot` records user-facing intent and binding status, `VolumeSnapshotClass` records driver parameters and deletion policy, and `VolumeSnapshotContent` records provisioned or pre-provisioned snapshot handles and binding to a namespaced snapshot. The `v1beta1` served version keeps older clients usable while `v1` is the stored version.

## Dependencies and Integration Points
The file depends on Kubernetes apiextensions v1 and a cluster new enough to serve CRD structural schemas. It integrates with `csi-snapshot-controller.yaml`, `rbac-snapshot-controller.yaml`, the `csi-snapshotter` sidecar in the NFS controller deployment, and the NFS CSI driver name `nfs.csi.k8s.io` used by snapshot classes and contents.

## Risks and Test Signals
Risks include cluster-wide CRD replacement impact, schema drift with the snapshot-controller image version, and backwards compatibility exposure from serving both `v1` and `v1beta1`. Test signals are successful `kubectl apply`, `kubectl get crd volumesnapshots.snapshot.storage.k8s.io`, discovery of both served versions, status-subresource updates by the snapshot controller, and a real PVC snapshot reaching `readyToUse=true`.
