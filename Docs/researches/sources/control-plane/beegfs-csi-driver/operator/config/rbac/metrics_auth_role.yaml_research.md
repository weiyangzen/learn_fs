<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/metrics_auth_role.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/metrics_auth_role.yaml

## Purpose
Authorizes the metrics server to perform Kubernetes authentication and authorization reviews.

## Important APIs, Types, And Functions
ClusterRole grants create on `authentication.k8s.io/tokenreviews` and `authorization.k8s.io/subjectaccessreviews`.

## Control Flow
controller-runtime secure metrics filter uses these APIs to validate scrape requests.

## State And Persistence
ClusterRole persists cluster-wide review permissions.

## Dependencies And Integration Points
Bound to manager service account by `metrics_auth_role_binding.yaml`; used by `main.go` metrics filter provider.

## Risks And Edge Cases
Without this role, authenticated metrics requests can fail. It grants sensitive review creation but not object access.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/metrics_auth_role.yaml -->
