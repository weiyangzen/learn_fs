# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-http-service.yaml

Purpose: optionally exposes provisioner/controller liveness metrics through a Service.

Important APIs/types/functions: gated by `.Values.provisioner.httpMetrics.service.enabled`; supports annotations, clusterIP, external IPs, load balancer settings, service type, and maps service port to `.Values.provisioner.httpMetrics.containerPort`.

Control flow: selects provisioner Deployment pods by app/component/release labels.

State and persistence behavior: Service object state only.

Dependencies and integration points: Prometheus/ServiceMonitor integration and debugging of controller health.

Risks: metrics endpoints may be unintentionally exposed with non-ClusterIP settings. No endpoints appear if labels differ from the Deployment.

Test signals: endpoint population and Prometheus scrape checks.
