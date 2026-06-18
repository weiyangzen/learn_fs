# sources/control-plane/csi-driver-smb/deploy/v1.9.0/csi-smb-controller.yaml

## Purpose
Controller Deployment for SMB CSI v1.9.0.

## Important APIs, Types, and Functions
Matches v1.8.0 controller structure with `smbplugin:v1.9.0`, external-provisioner v3.2.0, livenessprobe v2.7.0, health `29642`, metrics `29644`, and kube-system leader election.

## Control Flow
External-provisioner invokes the controller service over the shared `/csi/csi.sock`; the SMB container serves controller, identity, and optionally node APIs.

## State and Persistence
Uses an ephemeral socket `emptyDir`; persistent effects are PV/PVC objects, events, leases, and SMB-backed subdirectories created during provisioning.

## Dependencies
Depends on v1.9.0 image, RBAC, Linux scheduling, and storage sidecar compatibility.

## Integration Points
Coordinates with v1.9.0 node DaemonSets and CSIDriver. Controller create/delete paths internally call node stage/unstage code for SMB share access.

## Risks and Edge Cases
Privileged controller container and single replica remain notable. If internal mount operations fail, provisioning/deletion fails despite Kubernetes API permissions.

## Test Signals
Deployment readiness, liveness, metrics, leader election, and PVC create/delete/clone flows.
