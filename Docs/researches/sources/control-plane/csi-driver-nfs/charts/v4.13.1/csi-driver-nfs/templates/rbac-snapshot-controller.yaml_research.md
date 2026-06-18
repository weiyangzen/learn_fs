# sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose
This template creates the service account, cluster role, cluster role binding, leader-election role, and role binding for the optional CSI snapshot controller.

## Important APIs, Types, and Functions
When `externalSnapshotter.enabled` is true it emits a `ServiceAccount`, a cluster `snapshot-controller-runner` role, a cluster binding, and namespaced leader-election `Role`/`RoleBinding`. Rules cover PV/PVC reads, PVC updates, events, `VolumeSnapshotClass`, `VolumeSnapshotContent`, `VolumeSnapshotContent/status`, `VolumeSnapshot`, `VolumeSnapshot/status`, optional node reads for distributed snapshotting, and coordination leases.

## Control Flow, State, and Persistence
The entire RBAC set is tied to the snapshot controller enable flag. Cluster roles persist independently of pods and authorize snapshot object reconciliation. Leader-election role state is namespace-scoped and matches the controller Deployment's `--leader-election-namespace`.

## Dependencies and Integration Points
This file supports `csi-snapshot-controller.yaml` and requires snapshot CRDs to make the API resources meaningful. It integrates with `.Values.externalSnapshotter.enabledDistributedSnapshotting` even though the default values do not define that key.

## Risks and Test Signals
Risks include cluster-wide write/delete privileges on snapshot contents, missing RBAC if a separately installed snapshot controller is expected to run outside this release, and values drift around distributed snapshotting. Signals are `kubectl auth can-i` for snapshot resources, successful lease creation, controller logs without forbidden errors, and snapshot object status updates.
