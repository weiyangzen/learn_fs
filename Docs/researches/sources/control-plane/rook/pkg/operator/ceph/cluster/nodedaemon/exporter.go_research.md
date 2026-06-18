# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/exporter.go

## Purpose
This file builds and manages per-node `ceph-exporter` Deployments plus the metrics Service and ServiceMonitor used for Prometheus scraping.

## Important APIs, Types, And Functions
Constants define socket directory, default exporter args, default metrics port `9926`, service port name, and cephx identity/secret names. `(r *ReconcileNode) createOrUpdateCephExporter()` creates/updates node-specific exporter Deployments. Helpers include `getCephExporterChownInitContainer()`, `getExporterMetricsPort()`, `getCephExporterDaemonContainer()`, `MakeCephExporterMetricsService()`, `EnableCephExporterServiceMonitor()`, `applyCephExporterLabels()`, `deleteOrphanedExporterDeployments()`, `applyPrometheusAnnotations()`, `generateExporterEnvVar()`, and `exporterIsHost()`.

## Control Flow And State
Exporter reconciliation short-circuits when `Monitoring.MetricsDisabled` is true. Otherwise it requires the node hostname label, builds an owned Deployment, and creates or updates it. The pod uses recreate strategy, hostname node selector, chown init container, exporter container, keyring volume, default service account, optional log collector, optional host networking with corresponding DNS policy, short termination grace period, annotations, and scrape annotations unless custom exporter annotations are supplied. Container args include socket dir, metrics port, perf counter priority limit, stats period, and `--addrs ::` for dual-stack or IPv6.

`MakeCephExporterMetricsService` creates a ClusterIP Service selecting exporter app labels. `EnableCephExporterServiceMonitor` creates/updates a ServiceMonitor, applies monitoring/exporter labels, interval, selector, owner reference, and optional relabel config for `rook.io/managedBy`. `deleteOrphanedExporterDeployments` lists exporter Deployments and removes those whose `node_name` label points to a deleted node.

## Dependencies And Integration Points
The file depends on Kubernetes Deployments/Services, controller-runtime clients, Prometheus Operator ServiceMonitor APIs, Rook controller helpers, CephCluster monitoring spec, keyring volumes, Ceph version labels, and Rook logging. It integrates with node reconciliation, monitoring enablement, and Prometheus discovery.

## Risks And Test Signals
Risks include stale exporter Deployments after node deletion, port/ServiceMonitor mismatches, host-network override ambiguity, IPv6 bind behavior, selector immutability, and duplicate socket use during rolling updates. Recreate strategy and orphan cleanup address two of these. `exporter_test.go` covers create/update behavior, custom exporter args and port, log collector sidecar, IPv6 `--addrs`, metrics Service, ServiceMonitor relabel labels, and orphan deletion.
