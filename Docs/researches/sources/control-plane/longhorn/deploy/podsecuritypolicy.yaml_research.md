<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/podsecuritypolicy.yaml -->
# sources/control-plane/longhorn/deploy/podsecuritypolicy.yaml

Purpose: legacy PodSecurityPolicy and namespace RBAC allowing Longhorn pods to run with the privileges required for host storage operations.

Important APIs/types/functions: defines `policy/v1beta1` `PodSecurityPolicy` named `longhorn-psp`, an RBAC `Role` granting `use` on that PSP, and a `RoleBinding` for `longhorn-service-account` and the namespace `default` service account.

Control flow: clusters that still support PSP admit Longhorn pods through this policy when the bound service accounts create pods. The policy allows privileged mode, privilege escalation, `SYS_ADMIN`, hostPath volumes, host PID, and broad user/group/SELinux strategies while dropping `NET_RAW`.

State and persistence: it stores only admission policy and RBAC objects. There is no application data persistence, but the policy permits hostPath mounts used by Longhorn runtime pods.

Dependencies/integration points: depends on the removed `policy/v1beta1` PodSecurityPolicy API, so it only applies to older Kubernetes versions or distributions that retain PSP. It integrates with Longhorn service accounts in `longhorn-system`.

Risks/test signals: PSP is obsolete on modern Kubernetes, and the granted privileges are intentionally broad. Test signals are server-side apply against target cluster versions, pod admission checks for manager/instance pods, and verification that replacement Pod Security Admission labels or distribution-specific policies cover equivalent privileges.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/podsecuritypolicy.yaml -->
