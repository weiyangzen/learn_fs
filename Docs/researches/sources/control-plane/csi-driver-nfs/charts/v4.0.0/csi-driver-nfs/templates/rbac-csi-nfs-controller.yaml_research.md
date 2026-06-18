# sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/templates/rbac-csi-nfs-controller.yaml

Purpose: v4.0.0 controller RBAC for provisioning.

Important APIs/types/functions: Optional ServiceAccount, ClusterRole, ClusterRoleBinding; value-derived names; PV/PVC/storageclass/event/csinode/node/lease/secrets permissions.

Control flow: Service account and RBAC render behind independent values gates. The binding targets `csi-{{ .Values.rbac.name }}-controller-sa`.

State and persistence: Kubernetes service account and cluster RBAC.

Dependencies and integration points: Controller Deployment and provisioner sidecar.

Risks: Cluster-wide secret get remains broad, and no node service account is created in this older v4 file. Test signals: render and dry-run with RBAC gates and custom rbac name.
