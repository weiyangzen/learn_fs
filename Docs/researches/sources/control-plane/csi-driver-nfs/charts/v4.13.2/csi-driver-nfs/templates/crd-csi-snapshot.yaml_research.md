# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose
This file is the v4.13.2 snapshot CRD template for the NFS CSI chart. It installs `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` CRDs only when the chart is configured to run the external snapshotter and create CRDs.

## Important APIs, Types, and Functions
It emits three `apiextensions.k8s.io/v1` CRDs in `snapshot.storage.k8s.io`, with `v1` as the served storage version and non-served deprecated `v1beta1` schemas retained for conversion metadata. It uses OpenAPI validation, status subresources, printer columns, `oneOf` source selection, `Delete`/`Retain` deletion policy enums, and Helm `helm.sh/resource-policy: keep`.

## Control Flow, State, and Persistence
The top-level conditional is `and .Values.externalSnapshotter.enabled .Values.externalSnapshotter.customResourceDefinitions.enabled`. CRDs are cluster-scoped API definitions and will survive chart uninstall because of the keep annotation. Snapshot objects and status fields are then reconciled by the external snapshot controller and CSI snapshotter sidecar.

## Dependencies and Integration Points
This template integrates with the optional snapshot-controller Deployment/RBAC, the controller Deployment's `csi-snapshotter` sidecar, and optional `VolumeSnapshotClass` creation. It is byte-identical to the v4.13.1 version.

## Risks and Test Signals
Risks include ownership conflicts with platform-managed snapshot CRDs, disabling CRD creation in clusters without existing APIs, and stale retained CRDs during downgrade/upgrade testing. Signals include `helm template` with CRD flags, server-side dry-run, CRD discovery before controller readiness, and an end-to-end snapshot/restore workflow.
