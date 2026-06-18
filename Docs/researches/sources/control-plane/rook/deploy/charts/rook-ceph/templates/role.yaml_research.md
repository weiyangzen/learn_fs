
# sources/control-plane/rook/deploy/charts/rook-ceph/templates/role.yaml

Purpose: renders the namespace-scoped `rook-ceph-system` `Role` for the Helm-installed Rook Ceph operator when `.Values.rbacEnable` is true. It gives the operator authority to manage helper resources in the release namespace.

Important APIs/types/functions: Kubernetes `rbac.authorization.k8s.io/v1` `Role`, Helm `.Release.Namespace`, `.Values.rbacEnable`, and `include "library.rook-ceph.labels"`. Rules cover core `pods`, `configmaps`, and `services`; `apps`/`extensions` daemonsets, statefulsets, and deployments; `batch` cronjobs; `cert-manager.io` certificates and issuers; and `multicluster.x-k8s.io` serviceexports.

Control flow: Helm skips the entire document when RBAC is disabled. When rendered, the role is bound by `rolebinding.yaml` to the `rook-ceph-system` service account so the operator can create, update, watch, patch, and delete namespaced support objects while reconciling clusters and CSI/operator resources.

State and persistence: the Role is persisted as Kubernetes RBAC state. It stores no Ceph data, but changes immediately alter what the operator can mutate in its own namespace.

Dependencies/integration: depends on the chart library label helper, the matching service account and role binding, cert-manager only when certificate integration is used, and multicluster service export APIs only when multi-cluster service export is enabled.

Risks: permissions are broad inside the operator namespace, including workload deletion and `deletecollection`. Disabling RBAC assumes equivalent permissions already exist. Missing verbs can break reconciliation in ways that surface as operator errors rather than Helm failures.

Test signals: render with `rbacEnable=true` and `false`; verify labels and namespace; run `kubectl auth can-i` as `system:serviceaccount:<ns>:rook-ceph-system` for each resource group used by the operator.
