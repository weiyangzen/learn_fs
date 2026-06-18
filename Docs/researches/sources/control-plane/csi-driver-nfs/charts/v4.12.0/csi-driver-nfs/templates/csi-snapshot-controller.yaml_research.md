# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose
This template optionally deploys the upstream external snapshot controller when `externalSnapshotter.enabled` is true. It is separate from the NFS controller-side `csi-snapshotter` sidecar.

## APIs, Control Flow, and State
The template emits an `apps/v1` `Deployment` named by `externalSnapshotter.name`. It applies labels/annotations, replica count, rolling update strategy with `maxSurge: 0`, `minReadySeconds: 15`, Linux node selection, optional image pull secrets, controller-derived affinity/tolerations, seccomp defaulting, and a single snapshot-controller container with leader election in the release namespace.

## Dependencies and Integration Points
The controller requires snapshot CRDs, the service account and RBAC in `rbac-snapshot-controller.yaml`, and the image configured at `image.externalSnapshotter`. It watches `VolumeSnapshot`, `VolumeSnapshotContent`, and `VolumeSnapshotClass` resources and coordinates with CSI driver snapshotter sidecars.

## Risks and Test Signals
Many Kubernetes distributions already install a snapshot controller; enabling this chart copy can create duplicate controllers. If CRDs are absent, the controller is expected to fail readiness or exit. Test with Helm condition combinations, leader election lease creation, controller logs, and end-to-end snapshot provisioning.
