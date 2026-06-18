## sources/control-plane/rook/deploy/charts/rook-ceph/templates/cluster-rbac.yaml

Purpose: renders CephCluster-scoped service accounts, roles, and bindings in the operator namespace by including library templates.

Important template behavior: always includes `library.cluster.serviceaccounts`, `library.cluster.clusterrolebindings`, `library.cluster.roles`, and `library.cluster.rolebindings`. When `.Values.monitoring.enabled` is true it also includes monitoring role and rolebinding helpers.

Control flow: no local resource definitions beyond include ordering. It mirrors the cluster chart RBAC template for the common same-namespace operator/cluster installation case.

State and persistence: creates namespace/service-account/RBAC objects needed for Rook-managed Ceph daemons and monitoring integration.

Dependencies and integration points: tightly coupled to library chart helper names and monitoring value semantics. Risks: changes in library helpers affect both operator and cluster charts; monitoring RBAC must align with Prometheus ServiceMonitor/PrometheusRule behavior. Tests should render with monitoring enabled and disabled and compare library output.
