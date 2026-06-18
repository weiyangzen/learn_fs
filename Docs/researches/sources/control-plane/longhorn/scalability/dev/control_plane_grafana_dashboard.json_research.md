# sources/control-plane/longhorn/scalability/dev/control_plane_grafana_dashboard.json

## Purpose
Grafana dashboard JSON for "Longhorn Control Plane Scalability" (`uid` `OUbS8NYIl`). It observes Kubernetes workload startup behavior, Longhorn-system pod resource use, apiserver request rate, and etcd health under scalability tests. The dashboard uses Prometheus datasource `uid: prometheus`, dark style, schema version 37, five-minute refresh, and a single query variable `cluster` sourced from `label_values(etcd_server_has_leader, job)`.

## Important APIs, Types, and Queries
The file is declarative Grafana dashboard schema: top-level `templating`, built-in annotations, and `panels`. Key panel groups are row panels `Workload`, `Longhorn CPU and RAM`, and `ETCD`.

Workload panels query `kube_pod_info`, `kube_pod_status_ready_time`, `kube_pod_created`, `kube_pod_status_phase`, and `kube_pod_container_status_restarts_total` in namespace `default`. They expose pod counts, phase distribution, startup-time histogram, count of pods ready within or beyond four minutes, per-minute running transition rate, per-node pod density, top 100 slow-starting pods, and crashed pod count.

Longhorn resource panels query `node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate`, `container_memory_rss`, and `container_memory_working_set_bytes` for namespace `longhorn-system`, grouped by pod.

ETCD panels query the selected `$cluster` job for `etcd_server_has_leader`, watch/lease `grpc_server_started_total` minus `grpc_server_handled_total`, unary RPC rates/errors, `etcd_mvcc_db_total_size_in_bytes`, p99 WAL/backend commit histograms, process RSS, client and peer network byte rates, proposal failed/pending/committed/applied counters, daily leader-election changes, and p99 peer RTT.

## Control Flow
Grafana evaluates the dashboard variable first, then panel targets over the active time range. Row panels organize metrics but do not perform computation. Most panels are direct PromQL expressions; histogram and table panels depend on Grafana transformations/visualization defaults rather than custom code.

## State and Persistence
Dashboard state is entirely persisted in this JSON file: panel IDs, grid positions, datasource references, variable defaults, refresh interval, and annotation config. Runtime state lives in Grafana and Prometheus only. The dashboard assumes metrics history is retained by Prometheus and does not write application state.

## Dependencies and Integration Points
Requires Grafana schema v37 compatibility and a Prometheus datasource with `uid` `prometheus`. It integrates with kube-state-metrics, kubelet/cAdvisor recording rules, Kubernetes apiserver metrics, and etcd metrics. The `$cluster` variable assumes etcd jobs expose `etcd_server_has_leader`; default value is `kube-etcd`.

## Risks
The workload panels hard-code namespace `default`, so tests running elsewhere are invisible. The Longhorn resource panels hard-code namespace `longhorn-system`. The `cluster` variable is tied to etcd job labels and can silently miss metrics if the Prometheus job naming differs. Some queries use `OR vector(0)`, hiding absent series as zero. The startup-time expressions subtract timestamps and rely on kube-state-metrics readiness data being present and semantically compatible.

## Test Signals
Useful validation is `jq` parse success, Grafana import success, and Prometheus query preview for every panel. Operational test signals include non-empty pod startup panels during scalability workloads, Longhorn resource lines for active system pods, and etcd panels showing leader count and proposal/RPC activity for the selected cluster.
