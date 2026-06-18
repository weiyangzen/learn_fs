# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/values.yaml

## Purpose
This file defines the default values for chart 4.12.1 and is the main configuration surface for all templates.

## APIs, Control Flow, and State
It is identical to 4.12.0 except the NFS driver image tag changes from `v4.12.0` to `v4.12.1`. It keeps sidecars at csi-provisioner `v5.3.0`, csi-resizer `v1.14.0`, csi-snapshotter/snapshot-controller `v8.3.0`, livenessprobe `v2.17.0`, and registrar `v2.15.0`. It enables service account and RBAC creation, defaults FSGroup policy on, inline volume off, snapshotter sidecar on, external snapshot controller off, and StorageClass/SnapshotClass creation off.

## Dependencies and Integration Points
All templates read these values for names, images, scheduling, resources, feature gates, RBAC, and class creation. The image tag should align with `Chart.yaml` appVersion.

## Risks and Test Signals
The chart deploys driver components but no default StorageClass unless users opt in. Test chart rendering under default, storage-class-enabled, snapshot-controller-enabled, and control-plane scheduling overrides, and verify the 4.12.1 image is pulled.
