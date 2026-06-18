<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/monitoring/exporter-service-monitor.yaml -->
# sources/control-plane/rook/deploy/examples/monitoring/exporter-service-monitor.yaml

Purpose: Prometheus Operator `ServiceMonitor` for the Rook Ceph exporter.
Important APIs/types/functions: `ServiceMonitor` `rook-ceph-exporter`, selector labels `app: rook-ceph-exporter` and `rook_cluster: rook-ceph`, endpoint port `ceph-exporter-http-metrics`, path `/metrics`, and interval `10s`.
Control flow: Prometheus Operator discovers matching exporter Services in `rook-ceph` and scrapes metrics into Prometheus. State is monitoring configuration and Prometheus time-series data. Dependencies are exporter deployment/service enabled by Rook and Prometheus Operator CRDs. Risks: no targets if exporter disabled or labels differ, namespace comment substitutions must align, and scrape interval may need tuning. Test signals: Prometheus target Up, exporter metrics present, and labels include expected cluster identity.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/monitoring/exporter-service-monitor.yaml -->
