# sources/control-plane/ceph-csi/deploy/service-monitor.yaml

Purpose: sample Prometheus Operator `ServiceMonitor` for Ceph-CSI metrics.

Important APIs/types/functions: `monitoring.coreos.com/v1 ServiceMonitor` named `csi-metrics` in `rook-ceph`, label `team: rook`, selects Services with `app: csi-metrics` in namespace `default`, scraping `http-metrics` path `/metrics` every 5s.

Control flow: Prometheus Operator reconciles this object into scrape configuration for matching metrics Services.

State and persistence behavior: monitoring API object; no CSI runtime state.

Dependencies and integration points: requires Prometheus Operator CRD and Services from static manifests.

Risks: namespace and labels are examples and often need changes. Frequent 5s interval may be too aggressive in larger clusters.

Test signals: ServiceMonitor admission, Prometheus target discovery, and metrics availability.
