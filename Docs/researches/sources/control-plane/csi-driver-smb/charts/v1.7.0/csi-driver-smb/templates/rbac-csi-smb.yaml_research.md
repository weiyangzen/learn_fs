<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/rbac-csi-smb.yaml

- Purpose: Helm RBAC template for v1.7.0; it creates CSI SMB service accounts and ClusterRole/ClusterRoleBinding resources when `.Values.serviceAccount.create` and `.Values.rbac.create` are enabled.
- Important APIs/types/functions: emits `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`. The provisioner role grants PV/PVC/StorageClass/Event/CSINode/Node/Lease access plus read access to Secrets; later template shape includes a separate node ServiceAccount.
- Control flow: Helm renders names from `.Values.serviceAccount.*` and `.Values.rbac.name`; controller sidecars use the controller ServiceAccount for provisioning and leader election, while node pods use the node ServiceAccount when the chart creates it.
- State and persistence behavior: all state is Kubernetes RBAC and identity objects. No application data is stored, but these grants control which secrets and storage objects the CSI components can read or mutate.
- Dependencies/integration points: consumed by controller Deployment, Linux/Windows DaemonSets, CSI external-provisioner leader election, and secret-backed SMB credentials referenced by StorageClasses/PVs.
- Risks: cluster-wide Secret `get` is sensitive; insufficient Lease/Event/PV verbs cause provisioning failures; disabling RBAC creation requires equivalent pre-existing roles.
- Test signals: `helm template`/server-side dry-run plus a PVC provisioning attempt; RBAC denial messages in provisioner logs are the primary failure signal.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->
