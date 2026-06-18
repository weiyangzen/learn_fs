<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/prometheus/monitor.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/prometheus/monitor.yaml

## Purpose
Defines Prometheus Operator scraping configuration for manager metrics.

## Important APIs, Types, And Functions
ServiceMonitor `controller-manager-metrics-monitor` selects `control-plane: controller-manager`, scrapes `/metrics` over HTTPS using service account token auth and TLS verification.

## Control Flow
Prometheus Operator watches ServiceMonitor and creates scrape jobs for matching Services.

## State And Persistence
ServiceMonitor persists scrape configuration in the cluster.

## Dependencies And Integration Points
Requires monitoring.coreos.com/v1, the metrics service, and controller-runtime secure metrics endpoint.

## Risks And Edge Cases
References port `https`, but the metrics Service in this subset does not name its port. `insecureSkipVerify: false` requires serving cert trust to be correct.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/prometheus/monitor.yaml -->
