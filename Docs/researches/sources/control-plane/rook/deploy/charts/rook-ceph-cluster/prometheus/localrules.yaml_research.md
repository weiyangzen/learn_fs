## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/prometheus/localrules.yaml

Purpose: default Prometheus alert rules for locally managed Ceph clusters. The file is adapted from Ceph mixin alerts with Rook-specific changes, excluding cephadm alerts and adding/adjusting Prometheus scrape-job alerts.

Important rule groups: cluster health, monitors, OSDs, MDS/CephFS, mgr/prometheus module, placement groups, nodes, pools, health checks, hardware, Prometheus server scrape jobs, RADOS, generic daemon crashes, RBD mirror, NVMe-oF, and certificate manager. Alerts cover quorum risk, disk pressure, OSD down/full/flapping/read errors, PG unclean/damaged/unavailable, filesystem damage/offline/degraded/read-only, pool fullness/growth, slow ops, hardware failures, missing scrape jobs, RBD mirror sync problems, NVMe-oF scale/latency/security/interface concerns, and Ceph certificate warnings/errors.

Control flow: loaded by `templates/prometheusrules.yaml` when the CephCluster is not external. That template can override fields or disable individual rules by alert/record name.

State and persistence: rendered as PrometheusRule CR content; it affects alerting and operational response, not Ceph state. PromQL uses Ceph mgr/exporter metrics, node exporter metrics, kube metrics, and alert-template queries.

Dependencies and integration points: depends on monitoring being enabled, Prometheus Operator CRDs, Ceph mgr prometheus module/exporter metrics, node exporter, and consistent `cluster` labels. Risks: PromQL joins and label expectations are fragile across metric version changes; some alerts use Ceph health-detail names that may change with Ceph releases; broad rule volume can create noise unless overrides are tuned. Test signal should include render, YAML parse, and Prometheus rule validation.
