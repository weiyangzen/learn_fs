<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/metrics_auth_role_binding.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/metrics_auth_role_binding.yaml

## Purpose
Binds metrics auth review permissions to the manager service account.

## Important APIs, Types, And Functions
ClusterRoleBinding `metrics-auth-rolebinding` references ClusterRole `metrics-auth-role` and ServiceAccount `controller-manager`.

## Control Flow
Authorization checks use this binding when the manager handles secure metrics requests.

## State And Persistence
ClusterRoleBinding persists the cluster-wide subject/role link.

## Dependencies And Integration Points
Depends on service account and metrics auth ClusterRole.

## Risks And Edge Cases
Namespace rewrite must place the subject in the actual install namespace.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/metrics_auth_role_binding.yaml -->
