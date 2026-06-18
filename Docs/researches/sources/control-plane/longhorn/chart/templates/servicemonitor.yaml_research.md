# sources/control-plane/longhorn/chart/templates/servicemonitor.yaml

Purpose: optionally creates a Prometheus Operator ServiceMonitor for scraping Longhorn Manager metrics.

Important APIs/types/functions: `monitoring.coreos.com/v1` `ServiceMonitor`, `.Values.metrics.serviceMonitor.enabled`, additional labels, annotations, `sampleLimit`, selector `app: longhorn-manager`, namespace selector, endpoint port `manager`, interval, scrapeTimeout, relabelings, and metricRelabelings.

Control flow: when enabled, the template emits one ServiceMonitor in the release namespace. Optional scrape fields are rendered only when non-empty; `sampleLimit` uses a `with` block, so zero omits the field.

State and persistence: persistent CRD state consumed by Prometheus Operator. It does not itself scrape metrics; Prometheus instances select ServiceMonitors based on labels and operator configuration.

Dependencies/integration: depends on Prometheus Operator CRDs, a manager Service with port named `manager`, labels from manager service templates outside this subset, and any Prometheus selector conventions supplied via additional labels.

Risks: installing without the ServiceMonitor CRD fails. Incorrect additional labels can make Prometheus ignore the monitor. Endpoint port name must match the manager service. Aggressive intervals or missing sample limits can increase Prometheus load.

Test signals: render disabled/enabled, custom labels and annotations, interval/timeout, relabeling arrays, metric relabeling arrays, and nonzero sampleLimit. In-cluster, verify Prometheus target discovery and scrape success.
