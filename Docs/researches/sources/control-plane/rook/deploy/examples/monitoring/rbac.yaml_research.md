# sources/control-plane/rook/deploy/examples/monitoring/rbac.yaml

Purpose: grants Prometheus the namespace-scoped permissions needed to discover and scrape Ceph manager and exporter metrics in `rook-ceph`.

Important APIs/types/functions: three `Role`/`RoleBinding` pairs: `rook-ceph-monitor`, `rook-ceph-metrics`, and `rook-ceph-monitor-mgr`. They bind the `rook-ceph/prometheus` service account and are labeled to aggregate into the `prometheus` ClusterRole.

Control flow: Kubernetes RBAC authorizes the Prometheus service account to list/watch pods, services, endpoints, configmaps, and Ceph-related resources used by the scrape configuration and ServiceMonitor discovery.

State and persistence: persists RBAC policy only; no runtime state.

Dependencies/integration: complements `prometheus.yaml`; assumes the Prometheus service account lives in `rook-ceph` and that Prometheus Operator service discovery uses Kubernetes API watches.

Risks: namespace and service account names are hard-coded. Missing aggregation labels or RoleBindings will produce scrape discovery failures that look like empty target lists.

Test signals: `kubectl auth can-i --as system:serviceaccount:rook-ceph:prometheus list endpoints -n rook-ceph` and Prometheus target discovery for mgr metrics.
