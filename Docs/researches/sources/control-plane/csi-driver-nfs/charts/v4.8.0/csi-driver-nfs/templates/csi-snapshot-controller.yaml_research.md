# sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose
Optionally renders the snapshot-controller deployment for the v4.8.0 chart.

## Important APIs, Types, And Functions
Uses `apps/v1 Deployment`, `.Values.externalSnapshotter.*`, `.Values.image.externalSnapshotter`, optional image pull secrets, labels, annotations, resources, and leader election arguments.

## Control Flow
If the snapshotter is enabled, Helm emits a Linux deployment with `minReadySeconds: 15`, rolling update parameters, seccomp defaulting, and leader election in the release namespace. If disabled, it emits nothing.

## State And Persistence
No local storage. Runtime state consists of Kubernetes snapshot resources, events, and lease objects.

## Dependencies And Integration Points
Requires snapshot CRDs and RBAC, and coordinates with CSI sidecars in the controller deployment. The image tag is supplied by values and should match the CRD version.

## Risks And Edge Cases
This template is byte-identical across the three chart versions in this group. Duplicate cluster snapshot controllers can race. Missing CRDs cause readiness and reconcile failures.

## Test Signals
Render with snapshotter enabled, verify deployment readiness and leases, and exercise snapshot create/delete flows.
