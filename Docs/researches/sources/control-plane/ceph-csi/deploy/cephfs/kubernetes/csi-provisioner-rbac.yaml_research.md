# sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csi-provisioner-rbac.yaml

Purpose: static RBAC for CephFS provisioner/controller sidecars.

Important APIs/types/functions: creates `cephfs-csi-provisioner` ServiceAccount, ClusterRole for nodes, secrets, events, PV/PVC/status, storageclasses, volumeattachments/status, CSINodes, snapshots/status/classes, group snapshots/status/classes, replication CRDs, configmaps, serviceaccounts, and token creation; also namespace Role/RoleBinding for configmaps and leases.

Control flow: supports provisioning, attaching, resizing, snapshotting, group snapshots, replication integration, and leader election.

State and persistence behavior: RBAC objects authorize controllers that mutate Kubernetes storage state.

Dependencies and integration points: used by CephFS provisioner Deployment and external sidecars.

Risks: broad storage and secret privileges; hardcoded default namespace must be customized. Permissions must match enabled sidecars and CRDs.

Test signals: CephFS storage workflows and sidecar authorization logs.
