# sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose
Creates service accounts and core RBAC needed by the v4.7.0 CSI NFS controller and node components.

## Important APIs, Types, And Functions
Conditionally emits `ServiceAccount` objects when `.Values.serviceAccount.create` is true and a `ClusterRole` plus `ClusterRoleBinding` when `.Values.rbac.create` is true. Permissions cover PVs, PVCs, StorageClasses, snapshots, events, CSINodes, nodes, leases, and secrets.

## Control Flow
Helm controls whether accounts and RBAC are rendered. The controller service account is bound to a cluster role named from `.Values.rbac.name`, while the node account is created but not bound here because node operations mostly depend on registration and host access.

## State And Persistence
RBAC and service accounts are persistent cluster objects. They grant ongoing permissions to sidecars and remain until deleted by Helm or cluster operations.

## Dependencies And Integration Points
Integrates with `csi-nfs-controller.yaml`, `csi-nfs-node.yaml`, provisioner leader election, event recording, PV/PVC reconciliation, and optional snapshot sidecar behavior inside the controller deployment.

## Risks And Edge Cases
The provisioner role can create, patch, and delete PVs and update snapshot contents, so excessive namespace reuse or service-account sharing increases blast radius. Disabling RBAC requires equivalent external permissions.

## Test Signals
Use `kubectl auth can-i` for PV/PVC, lease, event, and snapshot verbs under the controller service account. Runtime failures appear as sidecar forbidden errors.
