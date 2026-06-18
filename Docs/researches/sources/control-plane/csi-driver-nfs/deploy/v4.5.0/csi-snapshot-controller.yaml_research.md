# sources/control-plane/csi-driver-nfs/deploy/v4.5.0/csi-snapshot-controller.yaml

## Purpose
This manifest deploys the v4.5.0 external snapshot controller. It updates the snapshot-controller image from v6.2.2 to v6.3.1 while keeping the same high-availability deployment shape.

## Important APIs, Types, and Functions
The object is an `apps/v1` `Deployment` named `snapshot-controller`, two replicas, `minReadySeconds: 15`, rolling update with no surge and one unavailable replica, Linux scheduling, control-plane tolerations, and `system-cluster-critical` priority. The single container runs `registry.k8s.io/sig-storage/snapshot-controller:v6.3.1` with verbosity 2 and leader election in `kube-system`.

## Control Flow, State, and Persistence
The elected replica watches and reconciles snapshot custom resources, while the second replica waits for failover. Persistent effects are updates to `VolumeSnapshot` and `VolumeSnapshotContent` status, events, finalizers, and leader-election lease state.

## Dependencies and Integration Points
It depends on the snapshot CRDs, snapshot-controller RBAC, and version-compatible `csi-snapshotter:v6.3.1` running in the NFS controller deployment. It uses shared API objects rather than direct access to the NFS driver.

## Risks and Test Signals
Risks include CRD/version skew, unavailable CRDs blocking readiness, and lease RBAC problems. Test signals are ready replicas, one active leader, no forbidden status updates, successful creation and binding of `VolumeSnapshotContent`, and snapshot status reaching ready.
