<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/role.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/role.yaml

## Purpose
Main ClusterRole for the BeeGFS CSI driver operator manager.

## Important APIs, Types, And Functions
Grants namespace object management for ConfigMaps, Secrets, ServiceAccounts, events, PVC/PV operations, apps DaemonSets/StatefulSets, BeegfsDriver resources/status/finalizers, RBAC creation/deletion/update, OpenShift privileged SCC use, CSIDriver creation/deletion, and read access to CSINodes/StorageClasses/nodes/pods.

## Control Flow
The controller uses these permissions while reconciling driver manifests and while granting driver runtime permissions.

## State And Persistence
ClusterRole persists broad operator privileges; actual runtime authorization comes from `role_binding.yaml`.

## Dependencies And Integration Points
Generated from kubebuilder RBAC markers in `beegfsdriver_controller.go` plus operator requirements.

## Risks And Edge Cases
This is intentionally high privilege. It can create RBAC and use privileged SCC, so namespace isolation and singleton enforcement matter. Some resources grant create/delete without update due to controller behavior.

## Test Signals
Envtest verifies the controller creates expected RBAC objects from deploy manifests, but authorization itself is not exercised.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/role.yaml -->
