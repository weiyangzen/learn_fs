<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/recovery-backend-network-policy.yaml -->
# sources/control-plane/longhorn/examples/network-policy/recovery-backend-network-policy.yaml

Purpose: ingress NetworkPolicy for Longhorn recovery backend pods.

Important APIs/types/functions: selects `longhorn.io/recovery-backend: longhorn-recovery-backend` and allows TCP port 9503 ingress without a `from` selector.

Control flow: policy allows any source to reach port 9503 on selected pods, while other ports are isolated if ingress isolation applies.

State and persistence: Kubernetes policy only.

Dependencies/integration points: depends on recovery backend labels, service port 9503, and CNI behavior.

Risks/test signals: open source scope may be broader than desired; tightening requires knowing all recovery clients. Test signals are recovery workflow connectivity and port-scoped network probes.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/recovery-backend-network-policy.yaml -->
