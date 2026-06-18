# sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-provisioner-rbac.yaml

Purpose: RBAC for NVMe-oF provisioner/controller sidecars.

Important APIs/types/functions: creates `nvmeof-csi-provisioner` ServiceAccount, ClusterRole for nodes, secrets, events, PV/PVC/status, storageclasses, volumeattachments/status, CSINodes, volumeattributesclasses, snapshots/status/classes, group snapshots/status/classes, replication CRDs, configmaps, serviceaccounts, and serviceaccount token creation; Role/RoleBinding for configmaps and leases.

Control flow: authorizes external-provisioner/resizer/attacher/snapshot-capable workflows and leader election.

State and persistence behavior: Kubernetes RBAC only.

Dependencies and integration points: bound to NVMe-oF provisioner Deployment service account.

Risks: broad permissions with default namespace references. Snapshot/group-snapshot permissions exist even though the static NVMe-oF provisioner manifest does not run snapshotter.

Test signals: sidecar authorization, provisioning/expansion/attachment workflows, and RBAC review.
