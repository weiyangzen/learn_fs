# sources/control-plane/longhorn/chart/templates/network-policies/webhook-network-policy.yaml

Purpose: optionally adds ingress policy for Longhorn admission webhook pods.

Important APIs/types/functions: Kubernetes `NetworkPolicy`, selector `longhorn.io/admission-webhook: longhorn-admission-webhook`, ingress policy type, and TCP port 9502.

Control flow: when network policies are enabled, the template emits one policy that selects admission webhook pods and allows ingress on TCP 9502 without restricting sources.

State and persistence: persistent state is a NetworkPolicy object. It affects Kubernetes API server or aggregator reachability to the webhook service, but webhook configuration objects are defined elsewhere.

Dependencies/integration: depends on the webhook service in `services.yaml`, labels on webhook pods, and CNI policy enforcement. It is deliberately less source-restrictive because API server source addresses are cluster-dependent.

Risks: open source access to port 9502 is broader than component-specific policies. Tightening it incorrectly could break API server admission calls because API server traffic may not carry pod labels or may originate from host network addresses.

Test signals: enable policies and create/update Longhorn CRs that trigger admission. Verify webhook service access from the API server and denial of non-9502 ports on webhook pods.
