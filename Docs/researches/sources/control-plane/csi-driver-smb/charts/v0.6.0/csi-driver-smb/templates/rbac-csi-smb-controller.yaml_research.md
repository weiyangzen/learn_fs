<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml

Purpose: renders service-account and cluster-scoped RBAC resources for SMB CSI controller-side and, in newer charts, node-side operations for release v0.6.0. Creation is gated by `.Values.serviceAccount.create` and `.Values.rbac.create`, so operators can bring their own identities and permissions.

Important APIs are Kubernetes `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`. The provisioner role grants PV/PVC, StorageClass, events, CSINode, node, secret, and leader-election lease access according to the sidecar generation used in this release. It creates only the controller service account and provisioner ClusterRole/Binding; node service accounts and inline-volume secret access are not represented in this early RBAC file.

Control flow is Helm conditional rendering: service accounts are emitted only when requested, RBAC is emitted only when requested, and inline-volume secret access in newer releases is tied to `.Values.feature.enableInlineVolume`. State is persisted as cluster RBAC objects and directly controls what the csi-provisioner, csi-resizer, and node plugin can read or mutate.

Dependencies and integration points include the external-provisioner, external-resizer, Kubernetes coordination leases for leader election, secret-backed SMB credentials, and the chart serviceAccount names. Risks are over-broad secret read access, missing lease verbs causing leader election failures, missing resizer RBAC when resizing is enabled, and name mismatches if users override service-account values. Test signals are `helm template` with RBAC toggles, Kubernetes SubjectAccessReview or `kubectl auth can-i`, sidecar leader-election logs, PVC provisioning/resize tests, and inline ephemeral volume mount tests when enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->
