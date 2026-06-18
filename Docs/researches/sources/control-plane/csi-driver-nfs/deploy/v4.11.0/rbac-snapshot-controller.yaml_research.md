# sources/control-plane/csi-driver-nfs/deploy/v4.11.0/rbac-snapshot-controller.yaml

Purpose: grants the external snapshot controller permission to watch and mutate Kubernetes snapshot resources and to coordinate leader election.

Important APIs/types/functions: the file creates service account `snapshot-controller`, ClusterRole `snapshot-controller-runner`, ClusterRoleBinding `snapshot-controller-role`, Role `snapshot-controller-leaderelection`, and matching RoleBinding in `kube-system`. Rules cover PV/PVC reads, PVC updates, Events, `VolumeSnapshotClass`, `VolumeSnapshot`, `VolumeSnapshot/status`, `VolumeSnapshotContent`, and `VolumeSnapshotContent/status`.

Control flow: once bound, snapshot-controller replicas can elect a leader, watch snapshot API objects, create and patch `VolumeSnapshotContent`, update `VolumeSnapshot` status, and emit Events. These permissions are separate from the NFS driver's own snapshotter sidecar RBAC.

State and persistence: the file persists security policy and leader-election access. Runtime snapshot state lives in the CRD objects updated under this authority.

Dependencies and integration points: required by `csi-snapshot-controller.yaml` and `crd-csi-snapshot.yaml`. It must be installed in the same namespace as the snapshot-controller deployment service account.

Risks: missing status verbs leave snapshots permanently pending. Cluster-scoped content update/delete permissions are powerful and should be limited to the snapshot controller service account. Namespace drift between service account, RoleBinding, and Deployment breaks leader election.

Test signals: `kubectl auth can-i` for snapshot resources as `system:serviceaccount:kube-system:snapshot-controller`, deployment rollout, and end-to-end snapshot create/delete with event inspection.
