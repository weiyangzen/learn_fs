# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/values.yaml

## Purpose
This is the default configuration contract for chart 4.13.0 and captures the main behavioral changes from 4.12.x.

## APIs, Control Flow, and State
It bumps the NFS image to `v4.13.0`, provisioner to `v6.1.0`, resizer to `v2.0.0`, snapshotter and snapshot-controller to `v8.4.0`, while keeping livenessprobe `v2.17.0` and registrar `v2.15.0`. Sidecar repositories move to `/sig-storage/...` entries combined with `image.baseRepo: registry.k8s.io`. It adds `controller.enableSnapshotCompression: true`, and a `nodeDriverRegistrar` block with optional liveness probe settings. Existing defaults for RBAC, service accounts, driver name, FSGroup policy, kubeletDir, scheduling, resources, external snapshotter, StorageClass, and SnapshotClass remain.

## Dependencies and Integration Points
Template changes in controller and node consume the new values. StorageClass examples remain documentation for NFS parameters and multiple class creation.

## Risks and Test Signals
Repository prefix logic makes image rendering sensitive to leading slashes. Snapshot compression changes storage behavior. New sidecar major versions need compatibility tests. Validate rendered images, feature gates, registrar liveness on/off, PVC lifecycle, expansion, snapshots, and upgrades from 4.12.x.
