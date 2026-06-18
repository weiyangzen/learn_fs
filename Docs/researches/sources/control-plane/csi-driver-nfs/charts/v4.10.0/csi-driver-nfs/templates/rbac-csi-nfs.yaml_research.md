# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

Purpose: v4.10.0 RBAC for CSI NFS controller/node identities, provisioner, resizer, and snapshot sidecar interactions.

Important APIs/types/functions: ServiceAccounts from `.Values.serviceAccount.controller` and `.Values.serviceAccount.node`; provisioner/resizer ClusterRoles and ClusterRoleBindings; snapshot API permissions.

Control flow: Service account creation is gated separately from RBAC. The provisioner role includes PV create/patch/delete, PVC update, storage class reads, snapshot reads/content updates/status updates, events, csinodes, nodes, leases, and secrets get. Resizer role handles PV/PVC/status/events/leases.

State and persistence: Cluster RBAC and service-account identities.

Dependencies and integration points: Controller Deployment sidecars depend on these permissions for provisioning, resizing, and snapshots.

Risks: Broad cluster-scoped rights and secrets read; RBAC does not gate snapshot permissions on snapshotter enablement. Test signals: sidecar startup logs, resize, provision, and snapshot authorization tests.
