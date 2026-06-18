# sources/control-plane/csi-driver-smb/deploy/v1.9.0/rbac-csi-smb.yaml

## Purpose
RBAC for SMB CSI v1.9.0.

## Important APIs, Types, and Functions
Defines controller/node service accounts, `smb-external-provisioner-role`, and controller binding. Grants PV/PVC, StorageClass, event, CSINode, node, lease, and secret access.

## Control Flow
Provisioner sidecar uses the controller account to watch and mutate storage resources, emit events, run leader election, and read credentials.

## State and Persistence
Persistent RBAC policy objects only.

## Dependencies
Requires Kubernetes RBAC, storage, core, and coordination APIs.

## Integration Points
Bound to v1.9.0 controller Deployment and referenced by v1.9.0 node DaemonSets.

## Risks and Edge Cases
Secret read permission is broad for a cluster role. Any namespace or service account name drift between manifests breaks provisioning.

## Test Signals
Authorization checks, leader-election lease, successful PVC provisioning/deletion, and event emission.
