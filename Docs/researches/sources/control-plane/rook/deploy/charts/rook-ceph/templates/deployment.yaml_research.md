## sources/control-plane/rook/deploy/charts/rook-ceph/templates/deployment.yaml

Purpose: renders the Rook Ceph operator Deployment.

Important template behavior: creates `rook-ceph-operator` with replicas `0` when `scaleDownOperator` is true, otherwise `1`; optional revision history; Recreate strategy; labels/annotations; priority/tolerations; operator image from `.Values.image`; args `ceph operator`; optional container security context; emptyDir mounts for `/var/lib/rook` and `/etc/ceph`; many env vars controlling namespace scope, concurrency, discovery daemon scheduling/resources, OpenShift hostpath privilege detection, custom hostname label, device hotplug, discovery interval, unreachable node toleration, and pod/node identity. It sets hostNetwork/dnsPolicy when requested, nodeSelector, service account when RBAC is enabled, and resources if provided.

Control flow: many optional value-driven env blocks, plus capability detection for OpenShift SCC behavior.

State and persistence: creates the long-running operator Deployment that reconciles all Rook Ceph resources. Runtime state is mostly in Kubernetes resources; pod-local config dirs are emptyDir.

Dependencies and integration points: depends on RBAC/service accounts, operator ConfigMap, CRDs, CSI/image settings, and Kubernetes/OpenShift capabilities. Risks: scaling operator to zero halts reconciliation; currentNamespaceOnly and RBAC scope must align; host network and privileged hostpath settings affect scheduling/security; discovery env values must parse correctly downstream. Tests should render common defaults, namespace-only, OpenShift, and scaled-down cases.
