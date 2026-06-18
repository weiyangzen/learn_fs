<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.5.0/rbac-csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.5.0/rbac-csi-smb-controller.yaml

- Purpose: v0.5.0 RBAC manifest for SMB CSI controller and node identities.
- Important APIs/types/functions: creates ServiceAccount, ClusterRole, and ClusterRoleBinding for the external provisioner. The role covers PV/PVC/StorageClass/Event/CSINode/Node/Lease access and Secret reads as required by the provisioner.
- Control flow: install scripts apply RBAC before controller and node workloads. CSI sidecars authenticate with these service accounts while reconciling volumes, leader-election Leases, Events, and secret-backed credentials.
- State and persistence behavior: persists Kubernetes identity and authorization rules only; it controls access to storage API objects and credential Secrets but stores no driver runtime data.
- Dependencies/integration points: consumed by `csi-smb-controller`, Linux/Windows node DaemonSets, external-provisioner, resizer where present, and StorageClass/PV secret references.
- Risks: broad Secret read and cluster-wide storage permissions are sensitive; missing resizer or node-secret rules cause runtime failures; historical controller-only RBAC does not cover newer node ServiceAccount patterns.
- Test signals: `kubectl auth can-i` for provisioner verbs, provisioning/resize attempts, and checking sidecar logs for RBAC denial events.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.5.0/rbac-csi-smb-controller.yaml -->
