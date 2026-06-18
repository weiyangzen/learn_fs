# sources/control-plane/rook/pkg/operator/ceph/cluster/monitoring.go

## Purpose
This file manages long-running Ceph cluster health monitoring goroutines for monitors, OSDs, and cluster status. It enables or cancels daemon-specific health checks based on the `CephCluster` health-check spec.

## Important APIs, Types, And Functions
`monitorDaemonList` contains `mon`, `osd`, and `status`. `(c *ClusterController) configureCephMonitoring(cluster, clusterInfo)` reconciles enabled monitoring routines. `isMonitoringEnabled(daemon, clusterSpec)` reads daemon-specific disabled flags. `(c *ClusterController) startMonitoringCheck(cluster, clusterInfo, daemon)` starts the appropriate health checker.

## Control Flow And State
`configureCephMonitoring` loops over the daemon list, computes whether each routine should be enabled, checks `cluster.monitoringRoutines` for existing `opcontroller.ClusterHealth`, and cancels running routines when now disabled. If no routine exists and monitoring is enabled, it creates a cancellable child context from the operator manager context, stores it, and starts the appropriate goroutine. Floating monitor clusters skip mon health checks because the monitor ID is not available in this path. OSD checks are skipped for external clusters.

## Dependencies And Integration Points
The code depends on cluster-local `sync.Map`-style monitoring routine storage, Rook `ClusterHealth` contexts, monitor health checker, OSD health monitor, Ceph status checker, and CephCluster health-check spec fields. It integrates with cluster reconciliation and operator manager lifecycle cancellation.

## Risks And Test Signals
Risks include leaking goroutines if cancellation state is not maintained, failing to restart a canceled routine because the entry remains in the map, and skipping mon monitoring for floating monitors. `monitoring_test.go` only covers `isMonitoringEnabled` for monitor enabled/disabled cases, so most goroutine lifecycle behavior is not unit-tested here.
