# sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose
Creates service accounts and controller RBAC for the v4.9.0 CSI NFS chart.

## Important APIs, Types, And Functions
Conditionally renders controller/node `ServiceAccount` resources plus the external provisioner `ClusterRole` and `ClusterRoleBinding`. Permissions include PV creation/deletion/patching, PVC updates, StorageClass reads, snapshot object access, event writes, CSINode and node reads, lease management, and secret reads.

## Control Flow
Service accounts and RBAC are gated separately. The controller service account is bound to cluster permissions when RBAC is enabled, while node service account creation supports the DaemonSet.

## State And Persistence
Authorization objects persist in the cluster and grant ongoing access to Kubernetes storage resources. They do not persist application data.

## Dependencies And Integration Points
Used by the v4.9.0 controller and node templates, csi-provisioner, csi-snapshotter, leader election, event recording, and secret-backed mount options.

## Risks And Edge Cases
Byte-identical to v4.7.0 and v4.8.0 here. The controller role has broad storage privileges. If RBAC is disabled, external roles must include all sidecar-required verbs.

## Test Signals
`kubectl auth can-i` for controller verbs and sidecar logs free of RBAC denial messages.
