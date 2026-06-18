# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose
This file renders RBAC for the optional v4.13.2 snapshot controller Deployment.

## Important APIs, Types, and Functions
It creates a snapshot-controller `ServiceAccount`, cluster role, cluster role binding, namespace `Role`, and namespace `RoleBinding` when `externalSnapshotter.enabled` is true. The cluster role grants snapshot class/content/snapshot read-write permissions, status updates, event writes, PV/PVC reads/updates, optional node reads, and lease permissions for leader election.

## Control Flow, State, and Persistence
All objects render only with the snapshot controller. Cluster-scoped permissions authorize reconciliation of snapshot API objects, while the namespace role controls leader-election leases in the release namespace.

## Dependencies and Integration Points
It supports the snapshot-controller Deployment and requires snapshot CRDs. The optional distributed snapshotting branch depends on `externalSnapshotter.enabledDistributedSnapshotting`, which is not present in the default values but can be supplied by users.

## Risks and Test Signals
Risks are over-privileged snapshot content access, duplicate controller installations, and undeclared optional values. Signals are authorization checks as the snapshot controller service account, lease creation, snapshot status updates, and controller logs under denied-RBAC scenarios.
