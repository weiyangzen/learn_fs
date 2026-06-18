# sources/control-plane/csi-driver-smb/deploy/v1.9.0/csi-smb-driver.yaml

## Purpose
CSIDriver object for SMB CSI v1.9.0.

## Important APIs, Types, and Functions
Defines driver name `smb.csi.k8s.io`, disables attach, and enables pod info on mount.

## Control Flow
Kubernetes uses it to route CSI calls to the node plugin without attach/detach controller operations.

## State and Persistence
Cluster-scoped CSIDriver state only.

## Dependencies
Requires storage.k8s.io/v1 and matching node registration.

## Integration Points
Matches manifests and Go driver constants for the SMB CSI driver name.

## Risks and Edge Cases
Driver name drift or absent CSIDriver can cause scheduling or mount behavior differences.

## Test Signals
CSIDriver existence, no attach operation creation, and pod metadata appearing in mount context.
