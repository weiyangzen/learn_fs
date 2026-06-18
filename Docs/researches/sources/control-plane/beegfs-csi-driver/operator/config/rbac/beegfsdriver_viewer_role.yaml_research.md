<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/beegfsdriver_viewer_role.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/beegfsdriver_viewer_role.yaml

## Purpose
End-user ClusterRole for read-only BeegfsDriver access.

## Important APIs, Types, And Functions
Grants get/list/watch on `beegfsdrivers` and get on `beegfsdrivers/status`.

## Control Flow
Applied with RBAC resources and later bound by admins as needed.

## State And Persistence
ClusterRole persists read permissions only.

## Dependencies And Integration Points
Targets CRD group `beegfs.csi.netapp.com`.

## Risks And Edge Cases
No write access; status may reveal deployment health and config metadata.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/beegfsdriver_viewer_role.yaml -->
