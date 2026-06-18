# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose
This optional Deployment runs the external snapshot controller for chart 4.13.0.

## APIs, Control Flow, and State
When enabled, it renders the same snapshot-controller Deployment structure as 4.12.x: release namespace, configurable labels/annotations, replicas, `minReadySeconds: 15`, rolling update, Linux selector, controller-derived affinity/tolerations, critical priority, seccomp, and leader election in the release namespace. It supports the 4.13 image repository convention where `/sig-storage/snapshot-controller` is prefixed by `image.baseRepo`.

## Dependencies and Integration Points
The controller integrates with snapshot CRDs and `rbac-snapshot-controller.yaml`. Its default image tag in 4.13.0 is `v8.4.0`, matching newer snapshot sidecars.

## Risks and Test Signals
The same duplicate-controller risk applies. Test rendering, image resolution, CRD readiness, leader election, and status reconciliation for snapshot create/delete flows.
