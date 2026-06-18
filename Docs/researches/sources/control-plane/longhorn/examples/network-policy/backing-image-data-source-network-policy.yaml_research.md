<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/backing-image-data-source-network-policy.yaml -->
# sources/control-plane/longhorn/examples/network-policy/backing-image-data-source-network-policy.yaml

Purpose: ingress NetworkPolicy for Longhorn backing image data source pods.

Important APIs/types/functions: selects pods with `longhorn.io/component: backing-image-data-source` and allows ingress from manager, instance manager, backing image manager, and other backing image data source pods.

Control flow: once applied in a policy-enforcing CNI, only matching peer pods can initiate ingress to selected data source pods.

State and persistence: stores network policy state in Kubernetes; no data persistence.

Dependencies/integration points: depends on labels emitted by Longhorn runtime pods and a CNI that enforces `networking.k8s.io/v1` policies.

Risks/test signals: missing required egress or external download allowances may still block workflows depending on cluster default policies. Test signals are backing image download/upload/clone flows and connectivity from each allowed component.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/backing-image-data-source-network-policy.yaml -->
