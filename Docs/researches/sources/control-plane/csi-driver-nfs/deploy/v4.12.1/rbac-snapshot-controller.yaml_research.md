<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.1/rbac-snapshot-controller.yaml

## Purpose
Defines RBAC for the external snapshot controller in the v4.12.1 bundle.

## Important APIs, Types, And Objects
Creates service account `snapshot-controller`, ClusterRole `snapshot-controller-runner`, ClusterRoleBinding `snapshot-controller-role`, Role `snapshot-controller-leaderelection`, and a matching RoleBinding. Rules cover PV/PVC reads and PVC update, event writes, `VolumeSnapshotClass` reads, `VolumeSnapshotContent` full lifecycle and status patch, `VolumeSnapshot` get/list/watch/update/patch/create, snapshot status update/patch, and Lease operations.

## Control Flow
The snapshot controller uses this policy to reconcile snapshot custom resources and coordinate active replicas. It creates or updates content objects, writes status, emits events, and maintains leader-election Leases.

## State And Persistence Behavior
The policy is durable Kubernetes RBAC state. It controls access to persistent snapshot API objects but stores no snapshot runtime data itself.

## Dependencies And Integration Points
References snapshot API resources supplied by `crd-csi-snapshot.yaml` and the service account used by `csi-snapshot-controller.yaml`.

## Risks And Edge Cases
Because the controller is shared, RBAC denial or over-permission affects all CSI snapshot workflows. Lease delete is allowed; ensure that is acceptable under local policy. Applying RBAC without CRDs is syntactically acceptable but does not make the controller usable until discovery succeeds.

## Test Signals
Use `kubectl auth can-i` for snapshot content create/delete, snapshot status update, event create, and Lease update. Then run snapshot lifecycle tests and inspect events/status transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/rbac-snapshot-controller.yaml -->
