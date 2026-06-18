# sources/control-plane/csi-driver-smb/deploy/v1.8.0/rbac-csi-smb.yaml

## Purpose
RBAC for SMB CSI v1.8.0 controller and node identities.

## Important APIs, Types, and Functions
Creates the same service accounts, cluster role, and controller binding as v1.7.0, granting PV/PVC, StorageClass, event, CSINode, node, lease, and secret access.

## Control Flow
External-provisioner uses these permissions during provisioning, deletion, event recording, and leader election.

## State and Persistence
Cluster RBAC objects persist until removed.

## Dependencies
Depends on RBAC and coordination APIs in Kubernetes.

## Integration Points
Consumed by v1.8.0 controller and node manifests; secret `get` integrates with SMB credential retrieval.

## Risks and Edge Cases
Broad secret access on a cluster role remains the main security concern. Node service account still has no additional binding in this file.

## Test Signals
Provisioner lease acquisition, PVC lifecycle success, and authorization checks for listed resources.
