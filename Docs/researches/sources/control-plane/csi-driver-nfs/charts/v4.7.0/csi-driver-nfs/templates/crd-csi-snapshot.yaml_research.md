# sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose
Helm template for installing CSI external-snapshotter CRDs with the v4.7.0 NFS chart. It is gated by `externalSnapshotter.enabled` and `externalSnapshotter.customResourceDefinitions.enabled`, so snapshot APIs are only emitted when the chart is asked to manage them.

## Important APIs, Types, And Functions
Defines Kubernetes `CustomResourceDefinition` objects for `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` in `snapshot.storage.k8s.io`. Each CRD serves `v1`, keeps deprecated `v1beta1` schemas as non-storage/non-served compatibility definitions, exposes printer columns, and uses status subresources where relevant.

## Control Flow
At render time Helm either emits all three CRDs or nothing. Once applied, Kubernetes admission validates snapshot source one-of fields, required driver/deletion-policy/source/reference fields, restore-size formats, status fields, and class parameters.

## State And Persistence
CRDs persist as cluster-scoped API extensions and include `helm.sh/resource-policy: keep`, preventing Helm uninstall from deleting them. Snapshot resources created through these CRDs persist cluster state for PVC snapshots and their backing CSI handles.

## Dependencies And Integration Points
Requires `apiextensions.k8s.io/v1`, the snapshot controller, csi-snapshotter sidecar, and CSI drivers using `CreateSnapshot`, `ListSnapshots`, and snapshot content binding semantics. It integrates with the chart's optional snapshot controller and RBAC templates.

## Risks And Edge Cases
Installing CRDs from a workload chart can conflict with cluster-managed CRDs or newer external-snapshotter versions. Keeping CRDs on uninstall avoids data loss but leaves lifecycle drift. Consumers must verify bidirectional `VolumeSnapshot` and `VolumeSnapshotContent` binding before restore.

## Test Signals
Primary signal is `helm template` with both snapshot flags enabled, followed by Kubernetes dry-run or CRD schema validation. Runtime signals are successful snapshot controller startup and accepted `VolumeSnapshot` objects.
