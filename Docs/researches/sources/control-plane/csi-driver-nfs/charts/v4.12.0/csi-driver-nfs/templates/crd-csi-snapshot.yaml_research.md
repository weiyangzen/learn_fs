# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose
This Helm template conditionally installs CSI snapshot CRDs when both `externalSnapshotter.enabled` and `externalSnapshotter.customResourceDefinitions.enabled` are true. It defines `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` in `snapshot.storage.k8s.io`, with `helm.sh/resource-policy: keep` so Helm uninstall does not remove cluster-wide snapshot APIs.

## APIs, Control Flow, and State
The template emits three `apiextensions.k8s.io/v1` `CustomResourceDefinition` objects. `VolumeSnapshot` is namespaced and models user snapshot requests from either a PVC or pre-existing content. `VolumeSnapshotClass` is cluster-scoped and stores driver, deletion policy, and opaque parameters. `VolumeSnapshotContent` is cluster-scoped and represents the bound physical snapshot handle or source volume. The schema serves and stores `v1`; `v1beta1` remains present but deprecated and not served/stored. Status subresources persist readiness, errors, creation time, restore size, and binding references.

## Dependencies and Integration Points
The CRDs are consumed by the external snapshot controller, the NFS CSI snapshotter sidecar, Kubernetes API discovery, and user-created `VolumeSnapshot*` resources. They integrate with `snapshotclass.yaml`, `rbac-snapshot-controller.yaml`, and controller RBAC rules that watch and update snapshot resources.

## Risks and Test Signals
Cluster-scoped CRDs can conflict with CRDs installed by another chart or distribution; the keep policy also means upgrades and deletions need explicit CRD lifecycle care. Test with `helm template` for conditional rendering, `kubectl apply --dry-run=server`, and snapshot API discovery checks. Validate that `v1beta1` deprecation behavior matches supported Kubernetes versions.
