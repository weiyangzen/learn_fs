# sources/cloud-native/containerd/plugins/restart/monitor.go

## Purpose
Registers and runs the container restart monitor plugin, reconciling container restart labels against actual task status across namespaces.

## Important APIs, Types, And Functions
`Config` controls reconcile interval. `monitor.run`, `reconcile`, and `monitor` implement the polling loop. The config migration moves legacy `internal.restart` config to `container-monitor.restart`.

## Control Flow
Startup advertises restart capabilities, builds an in-memory containerd client, starts the monitor loop, and returns the monitor. Each loop lists namespaces, concurrently scans containers with restart status labels per namespace, computes start/stop changes based on desired status, task status, and `restart.Reconcile`, then concurrently applies changes.

## State And Persistence
Desired state and restart counters live in container labels. Actual task state lives in runtime/shims. The monitor itself holds only a client.

## Dependencies And Integration Points
Requires event and service plugins, uses containerd client APIs, namespaces, restart policy helpers, plugin config migration, and logging.

## Risks
Polling interval controls responsiveness. Namespace and change loops run concurrently and may race with user operations. A known issue is empty task status after failed/deleted tasks affecting `on-failure` reconciliation.

## Test Signals
No direct tests in this subset. Restart behavior requires integration tests with task lifecycle.
