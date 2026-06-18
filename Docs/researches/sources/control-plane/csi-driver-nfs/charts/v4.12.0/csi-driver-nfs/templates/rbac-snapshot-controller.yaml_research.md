# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose
This template conditionally creates the service account and RBAC needed by the standalone external snapshot controller.

## APIs, Control Flow, and State
When `externalSnapshotter.enabled` is true it emits a release-namespace `ServiceAccount`, a cluster role named `<externalSnapshotter.name>-runner`, a cluster role binding, a namespaced leader-election `Role`, and a `RoleBinding`. The cluster role can read PVs, read/update PVCs, write events, read snapshot classes, create/read/list/watch/update/delete/patch snapshot contents, patch snapshot content status, and read/update/patch/create snapshots and statuses. It optionally adds Node read permissions when `externalSnapshotter.enabledDistributedSnapshotting` is true, even though this value is not declared in the default values file.

## Dependencies and Integration Points
The Deployment in `csi-snapshot-controller.yaml` uses this service account and relies on lease permissions for leader election. The RBAC targets the CRDs from `crd-csi-snapshot.yaml`.

## Risks and Test Signals
If `enabledDistributedSnapshotting` is used without matching snapshot-controller support, permissions may not match runtime expectations. Duplicate snapshot controllers can race. Test `kubectl auth can-i` for snapshot resources and leases, then run snapshot create/delete flows and inspect status updates.
