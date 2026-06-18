# sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose

This template creates the v4.5.0 RBAC and service account for the optional external snapshot-controller. It renders only when `.Values.externalSnapshotter.enabled` is true.

## APIs, control flow, and state

The resources are a namespace service account, a cluster role, a cluster role binding, and a release-namespace role/rolebinding for leader election. The cluster role grants the snapshot controller read/write access to snapshot API resources and status subresources, PV/PVC reads and updates, and event writes. Optional distributed snapshotting adds Node read permissions. Lease objects store leader-election state.

## Dependencies and integration points

This RBAC is consumed by `csi-snapshot-controller.yaml` and depends on snapshot CRDs existing or being installed by `crd-csi-snapshot.yaml`. It coordinates with the NFS controller's `csi-snapshotter` sidecar and Kubernetes status subresources.

## Risks and test signals

The role is cluster-wide and can mutate snapshots in all namespaces. `enabledDistributedSnapshotting` is referenced but not present in default values, so behavior depends on an operator-supplied value. Test auth checks for every granted resource, leader election in the release namespace, enabled/disabled rendering, and end-to-end snapshot create/delete flows.
