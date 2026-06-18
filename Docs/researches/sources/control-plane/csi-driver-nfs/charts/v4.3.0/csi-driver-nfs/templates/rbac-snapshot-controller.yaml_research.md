# sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose
This template renders RBAC for the v4.3.0 optional snapshot controller.

## Important APIs, Types, and Functions
It creates a snapshot controller service account, cluster role, cluster role binding, namespace role, and namespace role binding. Rules cover PV/PVC/event access, snapshot classes, snapshot contents, snapshot content status, snapshots, snapshot status, optional node reads for distributed snapshotting, and leader-election leases.

## Control Flow, State, and Persistence
All objects render when `externalSnapshotter.enabled` is true. The role persists as cluster authorization for snapshot reconciliation, and the namespaced role supports leader election in the release namespace.

## Dependencies and Integration Points
It supports `csi-snapshot-controller.yaml` and requires the snapshot CRDs emitted by the companion CRD template. The role grants `volumesnapshots` update/patch but not `create` in this version.

## Risks and Test Signals
Risks include missing create permission if future controller behavior expects it, duplicate snapshot controller installs, broad snapshot content modification rights, and optional value `enabledDistributedSnapshotting` not being declared in defaults. Signals are controller logs without RBAC denials, lease checks, snapshot create/update/status flows, and `kubectl auth can-i` coverage.
