<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/webhook-network-policy.yaml -->
# sources/control-plane/longhorn/examples/network-policy/webhook-network-policy.yaml

Purpose: ingress NetworkPolicy for the Longhorn admission webhook endpoint.

Important APIs/types/functions: selects `longhorn.io/admission-webhook: longhorn-admission-webhook` and allows TCP port 9502 ingress without restricting source.

Control flow: Kubernetes API server or other clients can reach webhook port 9502 while other ports are isolated under ingress policy.

State and persistence: Kubernetes NetworkPolicy object only.

Dependencies/integration points: depends on webhook pod labels, webhook Service, admissionregistration configuration, and CNI support.

Risks/test signals: source unrestricted is permissive, but API server source selection is CNI/environment-specific. Test signals are admission webhook calls during Longhorn CR changes and port 9502 connectivity from API server path.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/webhook-network-policy.yaml -->
