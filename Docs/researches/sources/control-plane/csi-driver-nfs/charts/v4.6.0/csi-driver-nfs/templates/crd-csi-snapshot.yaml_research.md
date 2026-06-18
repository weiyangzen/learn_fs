# sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose

This v4.6.0 template installs the Kubernetes CSI snapshot CRDs for `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` when snapshot-controller and CRD installation are both enabled.

## APIs, control flow, and state

The template is structurally identical to v4.5.0 for the requested file. Helm renders it only under `and .Values.externalSnapshotter.enabled .Values.externalSnapshotter.customResourceDefinitions.enabled`. Each CRD is annotated with `controller-gen.kubebuilder.io/version: v0.8.0`, the snapshot API approval URL, and Helm `resource-policy: keep`. The schemas define v1 served/storage resources, deprecated non-served v1beta1 versions, status subresources, printer columns, immutable source/binding fields, deletion policy enums, CSI driver/source fields, readiness, restore size, creation time, error, and CSI snapshot handles.

## Dependencies and integration points

The CRDs integrate with the API server, the NFS controller's `csi-snapshotter` sidecar, the optional snapshot-controller deployment, and both CSI and snapshot-controller RBAC templates. They are cluster-scoped install-time resources even though `VolumeSnapshot` objects themselves are namespaced.

## Risks and test signals

Keeping CRDs on uninstall protects snapshot API data but can leave stale CRDs after removing the chart. Operators must ensure the CRDs exist when snapshot workflows are enabled but chart CRD rendering is disabled. Test enabled/disabled Helm rendering, server-side dry-run application, `kubectl explain volumesnapshot`, deprecated v1beta1 request warnings, status-subresource updates, and full snapshot create/delete/restore-size validation.
