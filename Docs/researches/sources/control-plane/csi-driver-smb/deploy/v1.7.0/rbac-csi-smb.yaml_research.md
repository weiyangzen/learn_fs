# sources/control-plane/csi-driver-smb/deploy/v1.7.0/rbac-csi-smb.yaml

## Purpose
RBAC and service accounts for the v1.7.0 SMB CSI controller and node components.

## Important APIs, Types, and Functions
Creates `csi-smb-controller-sa`, `csi-smb-node-sa`, `smb-external-provisioner-role`, and `smb-csi-provisioner-binding`. The role covers PV/PVC watch and mutation, StorageClass read, events, CSINodes, nodes, leader-election leases, and secret get.

## Control Flow
After apply, the controller service account can run external-provisioner workflows and retrieve secrets needed for dynamic provisioning. Node service account is defined for DaemonSets but no binding is present in this file.

## State and Persistence
Persists cluster-scoped RBAC objects. No runtime state beyond Kubernetes RBAC policy.

## Dependencies
Requires Kubernetes RBAC, coordination leases, storage APIs, and namespace `kube-system`.

## Integration Points
Used by controller and node manifests in the same release folder. Secret access supports SMB credentials in CSI Create/Delete paths.

## Risks and Edge Cases
Secret `get` is cluster role scoped when bound to the controller account, so namespace boundaries rely on provisioner request context. Node account has no explicit permissions here.

## Test Signals
`kubectl auth can-i` for controller operations, successful external-provisioner leader election, PVC provisioning, events, and secret retrieval.
