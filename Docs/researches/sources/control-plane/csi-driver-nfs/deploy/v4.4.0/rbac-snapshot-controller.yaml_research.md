# sources/control-plane/csi-driver-nfs/deploy/v4.4.0/rbac-snapshot-controller.yaml

## Purpose
This file grants the external snapshot controller the permissions required to reconcile Kubernetes CSI snapshot objects and to coordinate leader election.

## Important APIs, Types, and Functions
It creates the `snapshot-controller` service account, `snapshot-controller-runner` cluster role and binding, and a namespaced `snapshot-controller-leaderelection` role and binding in `kube-system`. The cluster role can read PVs, read/update PVCs, create/update/patch events, read snapshot classes, create/read/update/delete/patch snapshot contents, patch snapshot content status, read/update/patch snapshots, and update/patch snapshot status. The role grants full lease lifecycle verbs for leader election.

## Control Flow, State, and Persistence
The resources persist as Kubernetes authorization state. The snapshot-controller deployment uses them to watch snapshot API resources, bind snapshot contents, update status subresources, emit events, and maintain a lease so only one replica reconciles actively.

## Dependencies and Integration Points
It is paired with `csi-snapshot-controller.yaml` and the CRDs in `crd-csi-snapshot.yaml`. It integrates with the `snapshot.storage.k8s.io` API group and with the NFS CSI snapshotter sidecar through shared custom resources rather than direct pod-to-pod calls.

## Risks and Test Signals
Risks include missing status-subresource verbs, lease permissions scoped to the wrong namespace, and overbroad delete rights on snapshot contents. Test signals are absence of authorization errors in snapshot-controller logs, a valid leader-election lease, updates to `VolumeSnapshot.status`, event creation, and successful deletion of `VolumeSnapshotContent` objects under both Retain and Delete policies.
