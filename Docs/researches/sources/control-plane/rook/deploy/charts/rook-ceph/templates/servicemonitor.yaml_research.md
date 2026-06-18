
# sources/control-plane/rook/deploy/charts/rook-ceph/templates/servicemonitor.yaml

Purpose: optionally creates a Prometheus Operator `ServiceMonitor` named `csi-metrics` for Ceph CSI metrics.

Important APIs/types/functions: `monitoring.coreos.com/v1` `ServiceMonitor`, Helm condition `and .Values.monitoring.enabled .Values.csi.serviceMonitor.enabled`, `.Values.csi.serviceMonitor.namespace`, `.Values.csi.serviceMonitor.labels`, `.Values.csi.serviceMonitor.interval`, and chart labels.

Control flow: Helm renders nothing unless global monitoring and CSI service monitoring are both enabled. The ServiceMonitor may live in an override namespace while its `namespaceSelector.matchNames` targets the release namespace. It selects services with `app: csi-metrics` and scrapes port `csi-http-metrics` at `/metrics`.

State and persistence: the object persists as monitoring configuration consumed by Prometheus Operator. It stores no metrics itself; Prometheus stores scraped metrics elsewhere.

Dependencies/integration: requires the Prometheus Operator CRD, CSI metrics services labeled `app: csi-metrics`, and Prometheus label selectors that match either chart labels or user-provided labels.

Risks: enabling this without the CRD causes apply failures. A namespace override can produce a valid ServiceMonitor that Prometheus does not select. Label or port drift in CSI metrics services silently prevents scraping.

Test signals: render all combinations of `monitoring.enabled`, `csi.serviceMonitor.enabled`, namespace override, custom labels, and interval. In-cluster tests should confirm Prometheus discovers `csi-metrics` targets and scrapes `/metrics`.
