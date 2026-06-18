# sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose
This Helm template installs the CSI external-snapshotter CRDs for the NFS CSI chart when both `externalSnapshotter.enabled` and `externalSnapshotter.customResourceDefinitions.enabled` are true. It defines `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` resources in `snapshot.storage.k8s.io`.

## Important APIs, Types, and Functions
The key Kubernetes APIs are `apiextensions.k8s.io/v1` `CustomResourceDefinition`, namespaced `VolumeSnapshot`, cluster-scoped `VolumeSnapshotClass`, and cluster-scoped `VolumeSnapshotContent`. The schemas serve `v1` as storage and retain deprecated `v1beta1` entries with warning text but `served: false`. The template uses Helm conditionals and annotates CRDs with `api-approved.kubernetes.io`, `controller-gen.kubebuilder.io/version`, and `helm.sh/resource-policy: keep`.

## Control Flow, State, and Persistence
Rendering is all-or-nothing behind the two-value gate. Once applied, the CRDs persist cluster-wide and Helm is instructed to keep them during uninstall, so snapshot API state can outlive this chart release. The CRD schemas enforce immutable source selectors, bidirectional snapshot/content binding fields, deletion policies, status subresources, printer columns, and snapshot readiness/restore-size status.

## Dependencies and Integration Points
The CRDs are required by `csi-snapshot-controller.yaml`, `rbac-snapshot-controller.yaml`, the controller-side `csi-snapshotter` sidecar, and optional `snapshotclass.yaml`. They must be installed before snapshot controllers become ready.

## Risks and Test Signals
Main risks are cluster-wide ownership conflicts, incompatible pre-existing CRDs, and accidental disabling of CRD creation while enabling snapshot controllers in a cluster without snapshot APIs. Useful signals are `helm template` with both flags, `kubectl apply --server-side --dry-run=server`, `kubectl get crd volumesnapshots.snapshot.storage.k8s.io`, and a dynamic `VolumeSnapshot` reaching `readyToUse`.
