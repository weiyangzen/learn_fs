# sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

Purpose: Consolidated v4.1.0 RBAC template creating both controller and node service accounts plus controller provisioner RBAC.

Important APIs/types/functions: Optional ServiceAccounts, ClusterRole, ClusterRoleBinding; `.Values.rbac.name`, `.Values.serviceAccount.create`, `.Values.rbac.create`, and namespace.

Control flow: Service-account gate creates `csi-<rbac.name>-controller-sa` and `csi-<rbac.name>-node-sa`. RBAC gate creates one external-provisioner role and binds it to the controller account.

State and persistence: Service account identities and cluster authorization.

Dependencies and integration points: Controller and node pod serviceAccountName fields; provisioner sidecar.

Risks: The node service account receives no explicit RBAC here, which is usually fine for node plugin but should be verified. Controller binding does not cover resizer/snapshotter because those sidecars are not present yet. Test signals: render custom `rbac.name` and confirm pod service accounts match.
