# sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/templates/rbac-csi-nfs-controller.yaml

Purpose: v3.1.0 controller RBAC, adding secrets read access to the v3 provisioner role.

Important APIs/types/functions: Optional `ServiceAccount`, `ClusterRole`, `ClusterRoleBinding`; value-derived names from `.Values.rbac.name`.

Control flow: When enabled, creates the controller service account and a ClusterRole with PV/PVC/storageclass/event/csinode/node/lease permissions plus `secrets get`.

State and persistence: Persists cluster authorization for controller sidecars.

Dependencies and integration points: Enables provisioner secret use for StorageClass mount options and deletion workflows.

Risks: Secret read is cluster-wide in the role, so least-privilege deployments may need tighter custom RBAC. Test signals: render with `rbac.create` toggled and exercise StorageClass secret parameters.
