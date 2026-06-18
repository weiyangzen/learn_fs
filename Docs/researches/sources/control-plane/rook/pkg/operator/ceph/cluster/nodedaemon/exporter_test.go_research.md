# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/exporter_test.go

## Purpose
This file tests ceph-exporter Deployment, container, Service, ServiceMonitor label, host-network, IPv6, and orphan cleanup behavior.

## Important APIs, Types, And Functions
Helpers `assertCephExporterArgs()` and `assertCephExporterArgsWithPort()` validate exporter argument order and optional IPv6 args. Tests exercise `createOrUpdateCephExporter()`, `getCephExporterDaemonContainer()`, `MakeCephExporterMetricsService()`, `applyCephExporterLabels()`, and `deleteOrphanedExporterDeployments()`.

## Control Flow And State
`TestCreateOrUpdateCephExporter` creates then updates a node-specific Deployment, verifying node selector, labels, tolerations, host network, DNS policy, service account, priority class, default args, custom perf/stats args, and custom port. `TestCephExporterLogrotateContainer` enables log collection and verifies the log collector sidecar. `TestCephExporterBindAddress` runs many network/hostNetwork combinations and verifies IPv6/dual-stack adds `--addrs ::` independently of host-network choice. `TestServiceSpec` verifies metrics Service name, port, labels, selector, and custom port. `TestApplyCephExporterLabels` verifies ServiceMonitor relabel config only when `rook.io/managedBy` is present in exporter labels. `TestDeleteOrphanedExporterDeployments` verifies no-op, preserve live-node deployments, delete missing-node deployments, skip missing `node_name`, and mixed cases.

## Dependencies And Integration Points
The tests use controller-runtime fake clients, Prometheus Operator API types, Rook fake clientsets, Kubernetes core/apps types, and Rook schemes. They validate exporter integration with Kubernetes object generation and Prometheus scrape configuration.

## Risks And Test Signals
The tests strongly cover object spec regressions and stale deployment cleanup. They do not run an actual exporter or ServiceMonitor controller. There is a minor noise signal in `TestApplyCephExporterLabels` where `fmt.Printf("Hello1")` appears to be leftover debug output.
