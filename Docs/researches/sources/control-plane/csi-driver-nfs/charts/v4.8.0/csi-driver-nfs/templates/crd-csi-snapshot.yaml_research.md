# sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose
Installs the same external-snapshotter CRDs as the v4.7.0 chart, gated by `externalSnapshotter.enabled` and CRD management values.

## Important APIs, Types, And Functions
Defines `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` CRDs with v1 storage schemas, deprecated v1beta1 definitions, printer columns, OpenAPI validation, and status subresources.

## Control Flow
Helm emits all CRDs only when snapshotter and CRD installation are enabled. Kubernetes then handles validation, stored versions, status updates, and discovery for snapshot APIs.

## State And Persistence
The CRDs are cluster-scoped and annotated with Helm keep policy, so they survive chart uninstall. They define the persistent API surface for snapshot request, class, and content objects.

## Dependencies And Integration Points
Requires compatible external-snapshotter components and cluster support for `apiextensions.k8s.io/v1`. The snapshot controller and sidecar use these resources for binding PVC snapshots to CSI snapshot handles.

## Risks And Edge Cases
This file is byte-identical to v4.7.0 and v4.9.0 in this source set, so CRD behavior does not move with the chart image releases. Cluster-wide CRD ownership can conflict with separately installed snapshot APIs.

## Test Signals
Render with snapshot flags enabled, apply via dry-run, and verify snapshot resources can be created and reconciled by the configured controller.
