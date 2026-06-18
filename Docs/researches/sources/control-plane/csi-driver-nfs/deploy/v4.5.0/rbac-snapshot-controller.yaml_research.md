# sources/control-plane/csi-driver-nfs/deploy/v4.5.0/rbac-snapshot-controller.yaml

## Purpose
This v4.5.0 RBAC file authorizes the external snapshot controller. It is unchanged from the v4.4.0, v4.6.0, and v4.7.0 files in this subset.

## Important APIs, Types, and Functions
It defines the `snapshot-controller` service account, `snapshot-controller-runner` cluster role and binding, plus a namespaced lease role and binding. The rules cover PV/PVC reads and PVC updates, event writes, snapshot class reads, snapshot content full lifecycle and status patch, snapshot read/update/patch and status update/patch, and lease create/update/delete/list/watch/get.

## Control Flow, State, and Persistence
Authorization state persists in Kubernetes and gates the snapshot-controller reconciliation loop. The lease role supports active/passive behavior for the two-replica deployment.

## Dependencies and Integration Points
It is consumed by `csi-snapshot-controller.yaml` and depends on the snapshot API group provided by `crd-csi-snapshot.yaml`. It coordinates indirectly with the NFS CSI snapshotter sidecar through snapshot custom resources.

## Risks and Test Signals
Risks include missing subresource verbs, wrong leader-election namespace, and destructive permissions on snapshot contents. Test signals are no RBAC denials, a maintained leader lease, event creation, snapshot status transitions, and successful cleanup of snapshot content resources.
