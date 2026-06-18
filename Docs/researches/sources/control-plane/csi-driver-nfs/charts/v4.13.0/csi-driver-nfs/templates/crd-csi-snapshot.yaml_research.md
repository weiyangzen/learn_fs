# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose
This is the 4.13.0 optional CSI snapshot CRD template. It installs the same cluster snapshot API definitions as the 4.12.x chart when the external snapshotter and CRD creation flags are enabled.

## APIs, Control Flow, and State
It emits `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` CRDs in `snapshot.storage.k8s.io` with `v1` served/storage schemas and deprecated `v1beta1` schemas not served or stored. `VolumeSnapshot` stores namespaced snapshot intent and readiness. `VolumeSnapshotClass` stores cluster-scoped driver/deletion-policy configuration. `VolumeSnapshotContent` stores cluster-scoped physical snapshot binding, source, status, and error state. CRDs are annotated with `helm.sh/resource-policy: keep`.

## Dependencies and Integration Points
Snapshot controller, NFS CSI snapshotter sidecar, RBAC, generated snapshot classes, and user snapshot resources all depend on these CRDs. In this repository the CRD body is unchanged from 4.12.1.

## Risks and Test Signals
CRD ownership and versioning remain the main risk because CRDs are global and kept after uninstall. Test conditional rendering, server-side dry-run, discovery of `snapshot.storage.k8s.io/v1`, and snapshot lifecycle operations.
