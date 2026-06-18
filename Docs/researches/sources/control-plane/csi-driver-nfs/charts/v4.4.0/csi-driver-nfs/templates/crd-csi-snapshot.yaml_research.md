# sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose

This Helm template installs the CSI external-snapshotter CRDs when `.Values.externalSnapshotter.enabled` is true. It emits three `apiextensions.k8s.io/v1` `CustomResourceDefinition` objects in the `snapshot.storage.k8s.io` API group: namespaced `VolumeSnapshot`, cluster-scoped `VolumeSnapshotClass`, and cluster-scoped `VolumeSnapshotContent`. These resources are the API contract used by the NFS CSI controller sidecars and optional snapshot controller to request, bind, and track point-in-time volume snapshots.

## APIs, control flow, and state

The template has no runtime code; Helm controls rendering through a single conditional. The CRDs define `v1` as served/storage and retain deprecated `v1beta1` schemas as non-served/non-storage versions with deprecation warnings. `VolumeSnapshot.spec.source` uses `oneOf` to require either `persistentVolumeClaimName` for dynamic snapshots or `volumeSnapshotContentName` for pre-existing snapshots. Snapshot status persists controller-observed fields such as `boundVolumeSnapshotContentName`, `creationTime`, `readyToUse`, `restoreSize`, and `error`. `VolumeSnapshotClass` persists `driver`, `deletionPolicy`, and opaque `parameters`. `VolumeSnapshotContent` persists the binding to a `VolumeSnapshot`, CSI `driver`, `deletionPolicy`, source `volumeHandle` or `snapshotHandle`, optional `sourceVolumeMode`, and status including the CSI `snapshotHandle`.

## Dependencies and integration points

The CRDs are consumed by `csi-snapshotter` in the controller deployment, the optional external snapshot-controller deployment, and the RBAC templates granting access to `volumesnapshots`, `volumesnapshotclasses`, and `volumesnapshotcontents`. They also integrate with Kubernetes API server CRD validation, status subresources, printer columns, and CSI snapshot gRPC concepts such as `CreateSnapshot` and `ListSnapshots`.

## Risks and test signals

In v4.4.0, CRDs are tied only to `externalSnapshotter.enabled`; enabling the controller also creates cluster-wide CRDs, and disabling it prevents CRD installation even if users only want the APIs. This version does not set Helm's `resource-policy: keep`, so uninstall behavior can remove CRDs and potentially API objects depending on Helm and cluster behavior. Test by running `helm template` with `externalSnapshotter.enabled=true/false`, validating all three CRDs with `kubectl apply --dry-run=server`, and creating sample `VolumeSnapshot*` resources to confirm schema validation, status subresources, deprecated version handling, and RBAC alignment.
