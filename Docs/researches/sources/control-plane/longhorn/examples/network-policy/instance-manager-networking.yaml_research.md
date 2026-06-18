<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/instance-manager-networking.yaml -->
# sources/control-plane/longhorn/examples/network-policy/instance-manager-networking.yaml

Purpose: ingress NetworkPolicy for Longhorn instance manager pods.

Important APIs/types/functions: selects `longhorn.io/component: instance-manager` and allows ingress from manager, other instance managers, and backing image data source pods.

Control flow: restricts inbound traffic to the data-plane manager pods while preserving Longhorn control/data communications between allowed components.

State and persistence: Kubernetes policy object only.

Dependencies/integration points: depends on CNI enforcement and Longhorn runtime pod labels.

Risks/test signals: data engine communication paths are sensitive; an omitted peer can break attach, rebuild, or replica traffic. Test signals are volume attach, replica rebuild, engine/replica instance health, and backing image interactions.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/network-policy/instance-manager-networking.yaml -->
