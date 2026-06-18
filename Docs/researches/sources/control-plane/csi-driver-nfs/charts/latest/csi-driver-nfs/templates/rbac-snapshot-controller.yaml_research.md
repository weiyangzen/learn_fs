# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

Purpose: Optional RBAC for deploying the upstream external snapshot-controller with this chart.

Important APIs/types/functions: Kubernetes `ServiceAccount`, `ClusterRole`, `ClusterRoleBinding`, namespaced `Role`, and `RoleBinding`; Helm values `.Values.externalSnapshotter.enabled`, `.Values.externalSnapshotter.name`, `.Values.externalSnapshotter.enabledDistributedSnapshotting`, `.Release.Namespace`, and `include "nfs.labels"`.

Control flow: The entire file renders only when `externalSnapshotter.enabled` is true. It creates a runner ClusterRole for PV/PVC/events and snapshot.storage.k8s.io resources, optionally adds node read permissions for distributed snapshotting, then adds cluster and namespace leader-election bindings.

State and persistence: Persists snapshot-controller identity and authorization; leader-election state itself is stored in `coordination.k8s.io` Leases at runtime.

Dependencies and integration points: Paired with `csi-snapshot-controller.yaml` and CRDs from `crd-csi-snapshot.yaml`.

Risks: This deploys a cluster-level controller that may duplicate a platform-installed snapshot-controller. Missing CRDs causes controller startup failure. Test signals: render with `externalSnapshotter.enabled` true/false and run server-side dry-run on clusters with snapshot CRDs.
