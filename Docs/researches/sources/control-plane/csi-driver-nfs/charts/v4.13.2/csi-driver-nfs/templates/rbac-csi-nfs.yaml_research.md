# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose
This file renders service accounts and controller-side cluster RBAC for the v4.13.2 NFS CSI chart.

## Important APIs, Types, and Functions
It conditionally creates controller and node `ServiceAccount` objects, an `external-provisioner` `ClusterRole`, an `external-resizer` `ClusterRole`, and two `ClusterRoleBinding` objects. Provisioner rules cover PV/PVC create/update/delete flows, storage classes, CSINodes, nodes, events, leases, secrets, and snapshot content status updates. Resizer rules cover PV/PVC/status updates and events.

## Control Flow, State, and Persistence
`serviceAccount.create` and `rbac.create` independently gate object creation. RBAC is cluster-scoped and persists until explicitly removed by Helm. Controller sidecars use namespace service account tokens to exercise these permissions.

## Dependencies and Integration Points
The controller and node workloads reference the service account names in values. Lease permissions integrate with sidecar leader election, secret access supports CSI provisioner secret parameters, and snapshot permissions support snapshot-aware provisioning.

## Risks and Test Signals
Risks include broad permissions, name mismatches when bringing pre-created service accounts, and granting snapshot permissions in clusters without snapshot APIs. Signals are `kubectl auth can-i` checks, sidecar logs free of forbidden errors, PVC lifecycle tests, resizer tests, and snapshot status update tests.
