<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/monitoring/csi-metrics-service-monitor.yaml -->
# sources/control-plane/rook/deploy/examples/monitoring/csi-metrics-service-monitor.yaml

Purpose: Prometheus Operator `ServiceMonitor` for scraping CSI sidecar/node metrics.
Important APIs/types/functions: `monitoring.coreos.com/v1` `ServiceMonitor` `csi-metrics`, namespace `rook-ceph`, label `team: rook`, namespace selector `rook-ceph`, selector `app: csi-metrics`, endpoint port `csi-http-metrics`, path `/metrics`, and interval `5s`.
Control flow: Prometheus Operator converts this CR into scrape config for matching CSI metrics Services. State is Prometheus scrape configuration and time-series data outside this manifest. Dependencies are Prometheus Operator CRDs, CSI metrics Services with matching labels/port names, and Prometheus selection of this ServiceMonitor. Risks: high 5s scrape interval can increase load, label/port mismatch yields no targets, and namespace must match Rook deployment. Test signals: ServiceMonitor accepted, Prometheus target appears Up, and CSI metrics are queryable.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/monitoring/csi-metrics-service-monitor.yaml -->
