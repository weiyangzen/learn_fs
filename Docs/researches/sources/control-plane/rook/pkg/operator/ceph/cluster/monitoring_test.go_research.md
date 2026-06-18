# sources/control-plane/rook/pkg/operator/ceph/cluster/monitoring_test.go

## Purpose
This small test file verifies health monitoring enablement logic for Ceph monitors.

## Important APIs, Types, And Functions
`TestIsMonitoringEnabled` table-drives `isMonitoringEnabled(daemon, clusterSpec)` for daemon `mon`. It checks the default enabled state and the disabled state when `HealthCheck.DaemonHealth.Monitor.Disabled` is true.

## Control Flow And State
The test constructs in-memory `ClusterSpec` values only. It does not start monitoring goroutines, create contexts, or interact with Kubernetes.

## Dependencies And Integration Points
It depends on the Ceph API `ClusterSpec` and health-check spec types. It provides a narrow regression check for `monitoring.go`.

## Risks And Test Signals
The test confirms the default monitor health checker is enabled and that the monitor disabled flag is respected. OSD/status enablement and lifecycle behavior in `configureCephMonitoring` remain uncovered by this file.
