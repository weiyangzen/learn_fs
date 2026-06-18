# sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/templates/rbac-csi-nfs-controller.yaml

Purpose: v3.0.0 configurable controller RBAC and ServiceAccount.

Important APIs/types/functions: `ServiceAccount`, `ClusterRole`, `ClusterRoleBinding`; values `.Values.rbac.name`, `.Values.serviceAccount.create`, `.Values.rbac.create`, and `.Release.Namespace`.

Control flow: Creates a name-derived controller service account and external-provisioner ClusterRole when enabled. Permissions include PV/PVC/storageclass/event/csinode/node/lease access for provisioning and leader election.

State and persistence: Service account identity and cluster RBAC bindings persist until Helm uninstall.

Dependencies and integration points: Used by controller Deployment serviceAccountName and external-provisioner sidecar.

Risks: Name templating improves multi-release support but still grants cluster-wide PV/PVC authority. Secrets access is absent, limiting StorageClass secret workflows. Test signals: render with custom `rbac.name`, check binding subject, and run provisioner RBAC smoke.
