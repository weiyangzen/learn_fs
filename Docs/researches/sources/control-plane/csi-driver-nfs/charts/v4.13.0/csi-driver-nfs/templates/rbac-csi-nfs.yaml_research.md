# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose
This template creates controller/node service accounts and cluster roles for 4.13.0 NFS CSI sidecars.

## APIs, Control Flow, and State
It is unchanged from 4.12.x. `serviceAccount.create` controls two ServiceAccounts. `rbac.create` controls provisioner and resizer ClusterRoles plus bindings to the controller service account. Permissions cover PV/PVC lifecycle, StorageClass reads, snapshot resource reads and content/status updates, events, CSINodes, Nodes, leader-election leases, and secret reads.

## Dependencies and Integration Points
These permissions are used by the updated 4.13.0 sidecars, including newer provisioner/resizer versions with explicit `VolumeAttributesClass=false`. The node service account is referenced by the DaemonSet.

## Risks and Test Signals
New sidecar versions may require permission review even if the RBAC did not change. Test with sidecar logs, `kubectl auth can-i`, PVC create/delete, resize, and snapshot flows.
