<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/metrics_reader_role.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/metrics_reader_role.yaml

## Purpose
Defines read access to the manager metrics endpoint.

## Important APIs, Types, And Functions
ClusterRole `metrics-reader` grants get on non-resource URL `/metrics`.

## Control Flow
Used by Kubernetes authz checks for metrics consumers.

## State And Persistence
ClusterRole persists a reusable permission but has no subject binding in this file.

## Dependencies And Integration Points
Matches controller-runtime secure metrics endpoint.

## Risks And Edge Cases
Requires a separate binding for Prometheus or users. Without it, authenticated scrapes may be denied.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/metrics_reader_role.yaml -->
