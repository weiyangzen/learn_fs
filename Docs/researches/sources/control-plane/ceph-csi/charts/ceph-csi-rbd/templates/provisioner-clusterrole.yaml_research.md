# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-clusterrole.yaml

Purpose: renders cluster RBAC for the RBD provisioner/controller Deployment and sidecars.

Important APIs/types/functions: grants access to secrets, PVs/PVCs, storageclasses, events, endpoints, replication CRDs, snapshots, group snapshots when enabled, configmaps, serviceaccounts, PVC status for resizing, nodes, CSINodes, serviceaccount tokens, and volumeattributesclasses. Some rules are conditional on attacher/resizer/group-snapshot settings.

Control flow: external-provisioner, attacher, resizer, snapshotter, and Ceph-CSI controller use these permissions during provisioning, attachment, expansion, snapshotting, leader election, metadata updates, and DR integrations.

State and persistence behavior: RBAC state only; it authorizes controllers that mutate PV/PVC/snapshot API objects and Ceph-side resources.

Dependencies and integration points: bound to the provisioner service account and must align with enabled sidecars/features in `provisioner-deployment.yaml`.

Risks: broad secret and storage-object privileges are powerful. Conditional group snapshot RBAC must match sidecar feature-gate settings or operations fail.

Test signals: provisioning, expansion, snapshot, clone, group snapshot, and replication e2e tests.
