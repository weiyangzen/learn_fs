# sources/control-plane/longhorn/chart/templates/network-policies/instance-manager-networking.yaml

Purpose: optionally restricts ingress to `longhorn.io/component: instance-manager` pods, which host Longhorn engine and replica processes.

Important APIs/types/functions: Kubernetes `NetworkPolicy`, `.Values.networkPolicies.enabled`, instance-manager `podSelector`, ingress policy, and source selectors for manager, peer instance managers, backing-image managers, and backing-image data-source pods.

Control flow: enabling network policies renders a single ingress-only policy selecting instance-manager pods. It admits traffic from Longhorn control-plane and data-plane helper pods that need to manage or synchronize instances.

State and persistence: policy state is stored in Kubernetes. It affects runtime communication for engines/replicas and can indirectly affect volume availability and rebuilds.

Dependencies/integration: depends on Longhorn labels for instance managers and related pods, plus CNI support. It is a core piece of the chart's optional network isolation because many Longhorn data-path operations traverse instance-manager pods.

Risks: missing a required source label can interrupt volume attachment, rebuild, or backing image flows. The policy does not restrict ports, so all ports exposed by instance-manager pods are reachable from allowed selectors. NetworkPolicy behavior may be ineffective on CNIs that do not enforce it.

Test signals: exercise volume attach/detach, rebuild, snapshot, backup, and backing image paths with policies enabled. Confirm unexpected pods cannot connect to instance-manager endpoints while Longhorn-managed pods still can.
