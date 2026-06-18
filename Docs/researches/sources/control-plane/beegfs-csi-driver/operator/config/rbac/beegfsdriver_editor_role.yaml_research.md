<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/beegfsdriver_editor_role.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/beegfsdriver_editor_role.yaml

## Purpose
End-user ClusterRole for editing BeegfsDriver resources.

## Important APIs, Types, And Functions
Grants create/delete/get/list/patch/update/watch on `beegfsdrivers` and get on `beegfsdrivers/status`.

## Control Flow
Applied as part of RBAC overlays only when included by higher-level packaging or user binding.

## State And Persistence
ClusterRole persists permissions; it does not bind users by itself.

## Dependencies And Integration Points
Targets the BeegfsDriver CRD API group.

## Risks And Edge Cases
Editor can change singleton driver spec and trigger cluster-wide driver rollout, but cannot update status.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/beegfsdriver_editor_role.yaml -->
