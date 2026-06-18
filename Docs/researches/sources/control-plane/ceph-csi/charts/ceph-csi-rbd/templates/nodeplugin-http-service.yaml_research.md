# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/nodeplugin-http-service.yaml

Purpose: optionally exposes nodeplugin liveness/metrics over a Kubernetes Service.

Important APIs/types/functions: gated by `.Values.nodeplugin.httpMetrics.service.enabled`; supports annotations, clusterIP, externalIPs, loadBalancerIP/source ranges, service type, service port, and target container metrics port.

Control flow: selects DaemonSet pods by app/component/release labels and routes `http-metrics` traffic to the liveness-prometheus container.

State and persistence behavior: Service object state only.

Dependencies and integration points: used by Prometheus/ServiceMonitor and operators diagnosing nodeplugin health.

Risks: enabling external Service settings can expose metrics beyond the cluster. Label mismatches prevent endpoints from appearing.

Test signals: Helm rendering, endpoint population, and metrics scrape checks.
