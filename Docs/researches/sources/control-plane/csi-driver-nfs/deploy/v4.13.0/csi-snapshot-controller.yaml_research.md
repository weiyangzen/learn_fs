<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-snapshot-controller.yaml

## Purpose
Deploys the v8.4.0 external snapshot controller for the v4.13.0 NFS CSI bundle.

## Important APIs, Types, And Objects
The Deployment runs two `snapshot-controller:v8.4.0` replicas using service account `snapshot-controller`, leader election, `minReadySeconds: 15`, rolling update with `maxSurge: 0` and `maxUnavailable: 1`, Linux scheduling, cluster-critical priority, and runtime-default seccomp.

## Control Flow
The elected snapshot controller reconciles snapshot CRDs, creates/binds `VolumeSnapshotContent`, updates statuses, and coordinates with driver-specific CSI snapshotter sidecars such as the v8.4.0 sidecar in the NFS controller.

## State And Persistence Behavior
The controller writes persistent state to snapshot custom resources, statuses, events, and leader-election Leases. Pods have no durable local storage.

## Dependencies And Integration Points
Requires the snapshot CRDs and snapshot-controller RBAC. It should be version-compatible with `csi-snapshotter:v8.4.0` in the v4.13.0 controller deployment.

## Risks And Edge Cases
Startup depends on the v1 CRDs being available. The shared controller affects all CSI drivers in the cluster. Version upgrades from v8.3.0 should be checked for CRD and RBAC compatibility.

## Test Signals
Verify deployment rollout, leader election across two replicas, snapshot creation/deletion with NFS, and status updates after controller pod restarts. Compare behavior against v4.12.x before upgrade.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-snapshot-controller.yaml -->
