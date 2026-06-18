<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/role_binding.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/role_binding.yaml

## Purpose
Binds the main manager ClusterRole to the manager service account.

## Important APIs, Types, And Functions
ClusterRoleBinding `manager-rolebinding` references ClusterRole `manager-role` and ServiceAccount `controller-manager`.

## Control Flow
Kubernetes authorizes manager API calls through this binding.

## State And Persistence
Persists cluster-wide role binding state.

## Dependencies And Integration Points
Depends on `manager-role` and service account resources; kustomize rewrites subject namespace.

## Risks And Edge Cases
Because the role is broad, an incorrect subject namespace/name can either break the operator or accidentally authorize the wrong service account.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/role_binding.yaml -->
