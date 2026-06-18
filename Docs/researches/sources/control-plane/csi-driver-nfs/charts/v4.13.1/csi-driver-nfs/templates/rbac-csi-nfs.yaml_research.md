# sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose
This template creates service accounts and cluster RBAC for the NFS CSI controller and node components. It grants the external provisioner and resizer the permissions needed to manage PV/PVC lifecycle, events, leases, secrets, and selected snapshot objects.

## Important APIs, Types, and Functions
When `serviceAccount.create` is true it emits controller and node `ServiceAccount` objects using `.Values.serviceAccount.controller` and `.Values.serviceAccount.node`. When `rbac.create` is true it emits `ClusterRole` objects for `external-provisioner` and `external-resizer`, plus `ClusterRoleBinding` objects to the controller service account. The provisioner role includes PV/PVC/storageclass/csinode/node/event/lease/secret permissions and snapshot read/update/status permissions.

## Control Flow, State, and Persistence
RBAC rendering is independently gated from service account rendering, allowing externally managed service accounts or roles. Bindings persist cluster-wide and authorize controller sidecars through the release namespace service account. There is no runtime state beyond Kubernetes authorization objects.

## Dependencies and Integration Points
The controller Deployment references the controller service account; the node DaemonSet references the node service account. Snapshot permissions are required by the provisioner and snapshotter paths when snapshot features are enabled. Lease permissions support sidecar leader election.

## Risks and Test Signals
Risks include broad cluster-level access, mismatched service account names when `serviceAccount.create=false`, and granting snapshot permissions even when external snapshot features are disabled. Signals include `kubectl auth can-i` checks as the controller service account, sidecar logs without RBAC forbidden errors, successful PVC create/delete/resize, and successful snapshot operations.
