# sources/control-plane/longhorn/chart/templates/psp.yaml

Purpose: optionally creates legacy PodSecurityPolicy permissions for privileged Longhorn pods on Kubernetes versions that still support PSP.

Important APIs/types/functions: `policy/v1beta1` `PodSecurityPolicy`, namespace `Role`, `RoleBinding`, `.Values.enablePSP`, privileged and allowPrivilegeEscalation flags, `SYS_ADMIN`, hostPID, hostPath volumes, and subjects `longhorn-service-account` plus `default`.

Control flow: when `enablePSP` is true, the template emits the PSP, a Role granting `use` on that PSP, and a RoleBinding to the Longhorn and default service accounts in the release namespace.

State and persistence: PSP and RBAC objects persist in the cluster/namespace and govern pod admission for matching service accounts. PSP itself is cluster-scoped, while the role and binding are namespace-scoped.

Dependencies/integration: depends on Kubernetes PSP API availability, which was removed in Kubernetes 1.25. It supports Longhorn workloads needing privileged operations, hostPID, capabilities, and hostPath volumes.

Risks: enabling this on modern clusters fails because `policy/v1beta1/PodSecurityPolicy` is gone. Granting the `default` service account use of a privileged PSP expands privilege beyond Longhorn-managed pods. PSP is deprecated and should not be confused with Pod Security Admission labels.

Test signals: render with `enablePSP` false and true; install only on a PSP-capable cluster; verify Longhorn privileged pods admit; confirm modern clusters require the value off or replacement Pod Security Admission configuration.
