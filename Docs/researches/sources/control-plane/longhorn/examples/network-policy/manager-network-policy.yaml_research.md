<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/manager-network-policy.yaml -->
# sources/control-plane/longhorn/examples/network-policy/manager-network-policy.yaml

Purpose: ingress NetworkPolicy for Longhorn manager pods.

Important APIs/types/functions: selects `app: longhorn-manager` and allows ingress from manager, UI, CSI plugin, recurring-job-managed pods, job-task pods, and driver deployer pods.

Control flow: limits access to the manager API/service to known Longhorn components in `longhorn-system`.

State and persistence: Kubernetes NetworkPolicy object only.

Dependencies/integration points: depends on labels for Longhorn UI, CSI, jobs, recurring jobs, and deployer, plus CNI enforcement.

Risks/test signals: external clients, ingress, monitoring, or support tooling may be blocked unless separately allowed. Test signals are UI access to backend, CSI provisioning calls, recurring jobs, driver deployment, and manager peer communication.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/manager-network-policy.yaml -->
