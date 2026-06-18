# sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose
Optionally deploys the external snapshot controller for the v4.9.0 chart.

## Important APIs, Types, And Functions
Defines an `apps/v1 Deployment` named from `.Values.externalSnapshotter.name`, with configurable image, resources, labels, annotations, replicas, priority class, image pull secrets, and leader-election flags.

## Control Flow
Rendered only when `externalSnapshotter.enabled` is true. The deployment runs on Linux nodes, uses release-namespace leader election, and waits at least 15 seconds before readiness to account for CRD availability behavior.

## State And Persistence
No persistent volume state. It persists effects through snapshot resources, status updates, events, and leader election leases.

## Dependencies And Integration Points
Requires snapshot CRDs and RBAC from this chart or an equivalent cluster install. Coordinates with the CSI snapshotter sidecar in the controller deployment.

## Risks And Edge Cases
Byte-identical to previous chart versions in this group. Enabling it alongside a cluster-managed snapshot controller can produce duplicate reconciliation. CRD absence or version mismatch is a primary failure mode.

## Test Signals
Snapshot controller deployment readiness, lease acquisition, no forbidden errors, and successful snapshot API lifecycle tests.
