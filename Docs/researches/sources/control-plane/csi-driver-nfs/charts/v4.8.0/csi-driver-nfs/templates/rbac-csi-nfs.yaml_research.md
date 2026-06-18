# sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose
Creates the v4.8.0 chart's service accounts and core CSI NFS RBAC.

## Important APIs, Types, And Functions
Conditionally creates controller and node `ServiceAccount` resources plus a cluster role/binding for the external provisioner role. The role grants PV/PVC, StorageClass, snapshot, event, CSINode, node, lease, and secret read permissions as required by the sidecars.

## Control Flow
Rendered based on `.Values.serviceAccount.create` and `.Values.rbac.create`. The controller service account receives the cluster role; the node service account is available for the daemonset.

## State And Persistence
RBAC resources and service accounts persist as Kubernetes authorization state. They have no storage of their own but authorize mutations of durable PV and snapshot resources.

## Dependencies And Integration Points
Used by `csi-nfs-controller.yaml`, `csi-nfs-node.yaml`, csi-provisioner, csi-snapshotter sidecar, leader election, and event recording.

## Risks And Edge Cases
This file is byte-identical across v4.7.0, v4.8.0, and v4.9.0 here. Disabling RBAC shifts responsibility to the installer. Broad PV/snapshot permissions can be sensitive in shared clusters.

## Test Signals
`kubectl auth can-i` under the controller service account and absence of forbidden errors in provisioner/snapshotter logs.
