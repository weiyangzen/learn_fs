# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

Purpose: 4.11.0 RBAC for NFS CSI controller and node service accounts plus provisioner/resizer roles.

Important APIs/types/functions: ServiceAccount, ClusterRole, ClusterRoleBinding; values `.Values.serviceAccount.controller`, `.Values.serviceAccount.node`, `.Values.rbac.name`.

Control flow: Same as v4.10.0: service accounts gate independently from RBAC; provisioner role includes provisioning and snapshot permissions; resizer role covers resize/status/event/lease permissions.

State and persistence: Service-account identities and cluster RBAC.

Dependencies and integration points: Controller Deployment sidecars and node DaemonSet identity.

Risks: Broad cluster permissions and unconditional snapshot API permissions. Test signals: RBAC dry-run, provisioner/resizer/snapshot sidecar startup, PVC resize smoke.
