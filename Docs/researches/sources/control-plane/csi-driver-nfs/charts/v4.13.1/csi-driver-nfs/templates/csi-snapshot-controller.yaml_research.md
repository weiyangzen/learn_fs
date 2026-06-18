# sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose
This template optionally deploys the upstream CSI snapshot controller inside the NFS chart release. It provides the cluster control loop for binding `VolumeSnapshot` and `VolumeSnapshotContent` objects.

## Important APIs, Types, and Functions
It emits an `apps/v1` `Deployment` when `externalSnapshotter.enabled` is true. Values control the name, replicas, labels, annotations, image, pull policy, image pull secrets, priority class, resource requests/limits, and scheduling. The container runs snapshot-controller with leader election and namespace-scoped leader-election leases.

## Control Flow, State, and Persistence
The Deployment has `minReadySeconds: 15` so it is not considered ready before CRD discovery settles. It uses a rolling update with `maxSurge: 0` and `maxUnavailable: 1`. Scheduling can inherit controller affinity or generated control-plane/master affinity. Runtime state is primarily leader-election leases and snapshot API object status updates.

## Dependencies and Integration Points
It depends on snapshot CRDs, `rbac-snapshot-controller.yaml`, and the external snapshotter image configured in values. It works alongside the controller Deployment's `csi-snapshotter` sidecar; the controller handles Kubernetes object binding while the sidecar calls CSI snapshot operations.

## Risks and Test Signals
Risks are deploying a second snapshot controller in clusters that already provide one, enabling the controller without CRDs, and reusing controller scheduling/toleration knobs for a cluster-level component. Signals are snapshot-controller rollout, leader-election lease creation, no CRD discovery crash loops, and a `VolumeSnapshot` progressing to a bound content object.
