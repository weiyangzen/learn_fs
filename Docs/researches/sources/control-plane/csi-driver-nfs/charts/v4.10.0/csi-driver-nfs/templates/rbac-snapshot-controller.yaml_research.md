# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

Purpose: v4.10.0 optional RBAC for the external snapshot-controller.

Important APIs/types/functions: Snapshot-controller ServiceAccount, runner ClusterRole/Binding, namespaced leader-election Role/Binding, and optional node read permission for distributed snapshotting.

Control flow: Entire file is gated by `externalSnapshotter.enabled`. It grants read/update/create/delete/patch permissions across VolumeSnapshot, VolumeSnapshotContent, VolumeSnapshotClass, PVCs, PVs, events, and leases.

State and persistence: Cluster authorization and leader-election namespace authorization.

Dependencies and integration points: Used by `csi-snapshot-controller.yaml`; requires snapshot CRDs.

Risks: Cluster-wide snapshot controller permissions can conflict with existing controller installations. Test signals: enabled render, RBAC dry-run, and snapshot reconciliation smoke.
