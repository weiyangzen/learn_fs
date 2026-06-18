# sources/control-plane/longhorn/chart/templates/network-policies/backing-image-data-source-network-policy.yaml

Purpose: optionally restricts ingress to pods labeled `longhorn.io/component: backing-image-data-source`.

Important APIs/types/functions: Kubernetes `NetworkPolicy`, `.Values.networkPolicies.enabled`, `podSelector`, `policyTypes: Ingress`, and allowed `from` pod selectors for manager, instance manager, backing image manager, and peer backing image data source pods.

Control flow: when network policies are enabled, the template emits one ingress-only policy. It allows all ports from four intra-namespace Longhorn component selectors and denies other ingress to matching backing-image data-source pods by default.

State and persistence: persistent state is the NetworkPolicy object. It does not create pods or labels; policy enforcement depends on the cluster CNI implementation.

Dependencies/integration: depends on consistent labels applied by Longhorn Manager to backing-image data-source pods and related system-managed components. It complements the instance-manager and backing-image-manager policies.

Risks: label drift immediately breaks data-source downloads or synchronization. The policy does not include namespace selectors, so sources are same-namespace pod selectors by Kubernetes semantics. It also does not specify ports, so allowed sources can reach any exposed port on selected pods.

Test signals: with network policy enabled, verify backing-image creation and recovery workflows. Confirm traffic from manager, instance-manager, backing-image-manager, and peer data-source pods succeeds, while unrelated namespace pods are denied by the CNI.
