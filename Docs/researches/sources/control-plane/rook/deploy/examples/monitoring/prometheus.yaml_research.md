# sources/control-plane/rook/deploy/examples/monitoring/prometheus.yaml

Purpose: installs the example Prometheus service account, RBAC aggregation, binding, and Prometheus Operator `Prometheus` resource for scraping Rook/Ceph metrics.

Important APIs/types/functions: includes `ServiceAccount/prometheus`, `ClusterRole/prometheus` with aggregation selector `rbac.ceph.rook.io/aggregate-to-prometheus=true`, `ClusterRole/prometheus-rules` granting read access to Prometheus Operator resources, `ClusterRoleBinding/prometheus`, and `Prometheus/rook-prometheus`.

Control flow: the Prometheus Operator reconciles the `Prometheus` CR, uses `serviceMonitorSelector.matchLabels.team=rook` and `ruleSelector.matchLabels.role=alert-rules`, and runs the instance under the `prometheus` service account. RBAC aggregation lets Rook monitoring roles contribute permissions without editing the top-level role.

State and persistence: Prometheus runtime state is owned by the operator-managed pods; this manifest persists only Kubernetes objects and resource requests/limits.

Dependencies/integration: requires Prometheus Operator CRDs, `ServiceMonitor` objects such as `service-monitor.yaml`, `PrometheusRule` objects such as `localrules.yaml`, and monitoring RBAC from `rbac.yaml`.

Risks: empty or mismatched selectors silently result in no targets or rules. Cluster-wide RBAC is broad enough to read monitoring CRs across namespaces.

Test signals: `kubectl get prometheus rook-prometheus`, operator-created StatefulSet/pods, discovered ServiceMonitors, and loaded rules under the Prometheus UI.
