# sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csi-provisioner-rbac.yaml

Purpose: static RBAC for RBD provisioner/controller sidecars.

Important APIs/types/functions: creates `rbd-csi-provisioner`, ClusterRole for nodes, secrets, events, PV/PVC/status, storageclasses, snapshots/status/classes/content, volumeattachments/status, CSINodes, group snapshots/status/classes, replication CRDs, volumeattributesclasses, configmaps, serviceaccounts, and token creation; plus namespace Role/RoleBinding for configmaps and leases.

Control flow: authorizes dynamic provisioning, resizing, attachment, snapshots, group snapshots, DR metadata, leader election, and sidecar state updates.

State and persistence behavior: RBAC objects authorize mutation of Kubernetes storage API state.

Dependencies and integration points: used by `csi-rbdplugin-provisioner.yaml`.

Risks: broad storage and secret permissions; namespace defaults must be customized. Permission set must track enabled sidecars/features.

Test signals: RBD e2e provisioning, snapshot, resize, attach, replication, and group snapshot tests.
