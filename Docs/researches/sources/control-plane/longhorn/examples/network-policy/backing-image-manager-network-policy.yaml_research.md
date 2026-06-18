<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/backing-image-manager-network-policy.yaml -->
# sources/control-plane/longhorn/examples/network-policy/backing-image-manager-network-policy.yaml

Purpose: ingress NetworkPolicy restricting Longhorn backing image manager pods.

Important APIs/types/functions: selects `longhorn.io/component: backing-image-manager` and allows ingress from manager, instance manager, and backing image manager pods.

Control flow: policy-enforcing CNIs admit only selected peer pods to backing image manager pods.

State and persistence: only Kubernetes NetworkPolicy state.

Dependencies/integration points: depends on Longhorn backing image manager labels and CNI policy support.

Risks/test signals: incomplete peer list can break backing image synchronization. Test signals are backing image create, sync, transfer, and manager-to-manager connectivity checks.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/backing-image-manager-network-policy.yaml -->
