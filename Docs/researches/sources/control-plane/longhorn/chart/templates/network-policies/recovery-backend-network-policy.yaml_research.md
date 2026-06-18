# sources/control-plane/longhorn/chart/templates/network-policies/recovery-backend-network-policy.yaml

Purpose: optionally adds an ingress policy for Longhorn recovery backend pods.

Important APIs/types/functions: Kubernetes `NetworkPolicy`, selector `longhorn.io/recovery-backend: longhorn-recovery-backend`, ingress policy type, and TCP port 9503.

Control flow: if network policies are enabled, one NetworkPolicy is emitted. It selects recovery backend pods and allows ingress to TCP 9503 without a source restriction.

State and persistence: policy state persists in Kubernetes. Recovery backend runtime state is outside this template, but availability of port 9503 is controlled by this rule.

Dependencies/integration: depends on the recovery backend service in `services.yaml` and labels on recovery backend pods. It relies on the CNI's interpretation of a ports-only ingress rule.

Risks: because no `from` clause is specified, any source allowed by namespace/CNI defaults can reach port 9503 on selected pods. This may be intentional for recovery paths, but it is less restrictive than the manager and backing-image policies.

Test signals: enable network policies and verify recovery backend health and recovery workflows through service port 9503. Confirm non-9503 ports are denied and decide whether arbitrary source access to 9503 is acceptable for the cluster profile.
