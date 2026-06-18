# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose
This optional template deploys a standalone external snapshot controller for chart 4.12.1.

## APIs, Control Flow, and State
When `externalSnapshotter.enabled` is true it emits an `apps/v1` Deployment with release namespace, labels/annotations, replicas, selector, `minReadySeconds: 15`, rolling update strategy, Linux node selector, controller-derived affinity/tolerations, critical priority, seccomp, and one container running `snapshot-controller` with leader election in the release namespace.

## Dependencies and Integration Points
It depends on snapshot CRDs, RBAC in `rbac-snapshot-controller.yaml`, and the snapshot-controller image from values. It coordinates API-level `VolumeSnapshot*` resources separately from the NFS CSI sidecar that talks to the driver.

## Risks and Test Signals
Duplicating a cluster-provided snapshot controller can lead to competing reconciliation. Test that only one intended controller is active, CRDs are present before readiness, and snapshot statuses update correctly.
