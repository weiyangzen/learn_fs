# sources/control-plane/rook/deploy/examples/monitoring/service-monitor.yaml

Purpose: defines the Prometheus Operator `ServiceMonitor` that discovers the Ceph manager metrics service.

Important APIs/types/functions: `monitoring.coreos.com/v1` `ServiceMonitor/rook-ceph-mgr` in `rook-ceph`, labeled `team: rook`, with a namespace selector for `rook-ceph`, a service label selector for `app: rook-ceph-mgr` and `rook_cluster: rook-ceph`, and endpoint `http-metrics`.

Control flow: Prometheus in `prometheus.yaml` selects this monitor by label, then the operator expands it into scrape config for services matching the selector.

State and persistence: persists scrape discovery configuration as a Kubernetes CR; Prometheus stores scraped samples separately.

Dependencies/integration: requires the Rook Ceph manager service to expose a named metrics port and the Prometheus CR to select `team: rook`.

Risks: label drift on the mgr service or endpoint port rename breaks metrics collection without failing the manifest.

Test signals: ServiceMonitor appears in Prometheus targets, `rook-ceph-mgr` service labels match, and metrics such as `ceph_health_status` are present.
