# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose
This file is the 4.12.1 copy of the optional CSI snapshot CRD template. It installs the same `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` APIs when the external snapshotter and CRD creation flags are enabled.

## APIs, Control Flow, and State
The CRDs use `apiextensions.k8s.io/v1`, group `snapshot.storage.k8s.io`, and preserve CRDs on Helm uninstall. `VolumeSnapshot` is namespaced and tracks source PVC/content, class, bound content, readiness, restore size, and errors. `VolumeSnapshotClass` is cluster-scoped and requires driver plus deletion policy. `VolumeSnapshotContent` is cluster-scoped and stores physical snapshot source/handle, references, status, and restore size. `v1` is served/storage; `v1beta1` exists as deprecated not-served/not-storage schema.

## Dependencies and Integration Points
The CRDs are shared cluster infrastructure for the chart's optional snapshot controller, controller-side `csi-snapshotter`, generated snapshot class, and user snapshot resources. The 4.12.1 CRD content is identical to 4.12.0 in this tree.

## Risks and Test Signals
Installing CRDs from multiple charts can create ownership and upgrade conflicts; keeping CRDs means uninstall does not reset cluster state. Test rendering conditions, server-side dry-run, API discovery, and snapshot create/delete behavior against the installed snapshot controller.
