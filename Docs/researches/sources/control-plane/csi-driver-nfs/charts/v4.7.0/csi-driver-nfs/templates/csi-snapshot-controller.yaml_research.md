# sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose
Optionally deploys the external snapshot controller for the v4.7.0 chart when `.Values.externalSnapshotter.enabled` is true.

## Important APIs, Types, And Functions
Uses an `apps/v1 Deployment` named from `.Values.externalSnapshotter.name`. It supports custom labels/annotations, replica count, priority class, image pull secrets, resources, and the `snapshot-controller` image from `.Values.image.externalSnapshotter`.

## Control Flow
Helm emits nothing if snapshotter support is disabled. If enabled, Kubernetes rolls a Linux-only deployment with leader election in the release namespace. `minReadySeconds: 15` accounts for controller startup behavior when v1 CRDs are missing.

## State And Persistence
The deployment itself has no durable storage. Runtime state is held in snapshot API objects, events, and leader election leases. It watches PVCs, PVs, `VolumeSnapshot*` resources, and status subresources through RBAC.

## Dependencies And Integration Points
Requires snapshot CRDs, RBAC from `rbac-snapshot-controller.yaml`, and a controller image compatible with the installed CRDs. It coordinates with the NFS CSI `csi-snapshotter` sidecar, which performs CSI calls.

## Risks And Edge Cases
Enabling it in clusters that already provide a snapshot controller can create duplicate controllers. If CRDs are absent or incompatible, readiness and controller loops fail. The template reuses controller tolerations, so scheduling assumptions are inherited.

## Test Signals
Render with `externalSnapshotter.enabled=true`, verify deployment readiness, leader election lease creation, and successful `VolumeSnapshot` binding/status updates.
