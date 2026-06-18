# sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose

This template creates the service account and RBAC needed by the optional external snapshot-controller. It renders only when `.Values.externalSnapshotter.enabled` is true.

## APIs, control flow, and state

The template emits a namespace-scoped `ServiceAccount`, a cluster-wide `ClusterRole`, a `ClusterRoleBinding`, and a namespace-scoped `Role`/`RoleBinding` for leader election. The cluster role grants read access to PVs and snapshot classes, PVC list/watch/update, event writes, CRUD-style access to `VolumeSnapshotContent`, status patching, and `VolumeSnapshot` update/patch/status update. If `.Values.externalSnapshotter.enabledDistributedSnapshotting` is set, it also grants Node reads. Lease state persists in the release namespace through the namespaced role.

## Dependencies and integration points

The RBAC is consumed by `csi-snapshot-controller.yaml` and depends on snapshot CRDs being installed or already present. It coordinates with the `csi-snapshotter` sidecar and Kubernetes API status subresources to keep snapshot objects reconciled.

## Risks and test signals

This is cluster-scoped authority, so enabling the controller grants broad snapshot mutation across namespaces. The `enabledDistributedSnapshotting` value is referenced here but absent from the default v4.4.0 values, so users must add it explicitly if needed. Test with `kubectl auth can-i` for each snapshot resource and status subresource, leader-election lease operations in the release namespace, and end-to-end dynamic snapshot creation/deletion.
