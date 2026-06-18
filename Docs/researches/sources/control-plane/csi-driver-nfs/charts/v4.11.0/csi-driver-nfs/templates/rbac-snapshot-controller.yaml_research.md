# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

Purpose: 4.11.0 optional RBAC for external snapshot-controller.

Important APIs/types/functions: ServiceAccount, runner ClusterRole/Binding, leader-election Role/Binding; optional distributed snapshotting node reads.

Control flow: Rendered only when `externalSnapshotter.enabled` is true. Grants snapshot-controller authority over VolumeSnapshot*, PV/PVC/event resources and lease objects.

State and persistence: Cluster and namespace RBAC; runtime lease state is created by controller.

Dependencies and integration points: `csi-snapshot-controller.yaml` and snapshot CRDs.

Risks: Duplicate cluster-level snapshot controller and broad snapshot mutation permissions. Test signals: render enabled and run snapshot create/delete smoke.
