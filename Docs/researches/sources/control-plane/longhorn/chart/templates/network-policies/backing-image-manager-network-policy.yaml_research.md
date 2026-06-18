# sources/control-plane/longhorn/chart/templates/network-policies/backing-image-manager-network-policy.yaml

Purpose: optionally restricts ingress to pods labeled `longhorn.io/component: backing-image-manager`.

Important APIs/types/functions: Kubernetes `NetworkPolicy`, `.Values.networkPolicies.enabled`, backing-image-manager `podSelector`, ingress-only policy type, and allowed source selectors for manager, instance manager, backing image manager, and backing image data source pods.

Control flow: when enabled, one policy is rendered. It selects backing-image-manager pods and admits ingress from the Longhorn components that coordinate backing image file distribution and status.

State and persistence: the NetworkPolicy persists in the namespace and changes CNI-enforced pod connectivity. No storage state is directly stored here, but failures affect backing image files used by volume provisioning.

Dependencies/integration: depends on Longhorn's system-managed pod labels and the CNI's NetworkPolicy support. It works with the data-source and instance-manager policies to permit backing image traffic inside Longhorn.

Risks: a too-narrow selector set can break backing image operations, especially if future Longhorn components introduce new labels or paths. No port restrictions are present, so allowed pods receive broad ingress access.

Test signals: enable policies and create, sync, and delete backing images. Inspect denied traffic from unrelated pods and allowed traffic among manager, instance-manager, backing-image-manager, and data-source pods.
