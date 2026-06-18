<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/kustomization.yaml

## Purpose
Assembles service account and operator runtime RBAC.

## Important APIs, Types, And Functions
Includes service account, manager role/binding, leader election role/binding, metrics auth binding, and metrics reader role.

## Control Flow
The default overlay applies these resources before the manager deployment uses the service account.

## State And Persistence
RBAC objects persist in the cluster and authorize the operator process.

## Dependencies And Integration Points
Coordinates with `manager.yaml` service account name and RBAC annotations in the controller.

## Risks And Edge Cases
End-user editor/viewer roles are not included here, so they may only appear through generated bundle metadata or separate packaging. Any service account rename requires binding subject updates.

## Test Signals
Controller envtest checks RBAC objects produced by deploy manifests, not this kustomization directly.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/kustomization.yaml -->
