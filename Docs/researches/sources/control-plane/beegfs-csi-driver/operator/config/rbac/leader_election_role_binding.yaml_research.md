<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/leader_election_role_binding.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/leader_election_role_binding.yaml

## Purpose
Binds the leader election Role to the manager service account.

## Important APIs, Types, And Functions
RoleBinding `leader-election-rolebinding` references Role `leader-election-role` and subject ServiceAccount `controller-manager` in namespace `system`.

## Control Flow
Kustomize rewrites namespace/name as part of default install. Kubernetes authorization uses it during leader election calls.

## State And Persistence
RoleBinding persists the authorization relationship.

## Dependencies And Integration Points
Depends on the Role and service account resources.

## Risks And Edge Cases
Namespace placeholders must be rewritten consistently. A service account name change breaks leader election unless this binding changes too.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/leader_election_role_binding.yaml -->
