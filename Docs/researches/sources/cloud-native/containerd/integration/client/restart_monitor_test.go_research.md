<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/restart_monitor_test.go -->
# sources/cloud-native/containerd/integration/client/restart_monitor_test.go

## Purpose
Validates the container restart monitor plugin: always-restart behavior, paused task preservation, and on-failure retry counting.

## APIs, Types, And Functions
The file defines `newDaemonWithConfig`, `TestRestartMonitor`, `testRestartMonitorAlways`, `testRestartMonitorPausedTaskWithAlways`, `testRestartMonitorWithOnFailurePolicy`, and `convertTaskCreateEvent`. It uses server config loading, `restart.WithStatus`, `restart.NewPolicy`, `restart.WithPolicy`, client task lifecycle APIs, event subscription, container labels, and typeurl unmarshalling of `TaskCreate`.

## Control Flow And State
`newDaemonWithConfig` writes a temporary config, loads it to discover or synthesize an address, starts a daemon with temp root/state, waits for plugin readiness, and returns a cleanup closure. `TestRestartMonitor` enables `io.containerd.monitor.container.v1.restart` with a five-second interval, pulls the test image, then runs subtests. The always policy kills a running task and polls until it is running again before the deadline. The paused-task case pauses and ensures the monitor does not kill/restart it. The on-failure case starts an exit-1 task with `on-failure:1`, waits for a `/tasks/create` event, and checks restart count label equals one.

## Persistence And Integration Points
State spans temporary daemon config/root/state, task status, restart labels, event streams, and restart monitor plugin state. It integrates the client API with daemon plugin configuration and task event publication.

## Risks And Test Signals
Timing is the main risk: slow shutdown/restart can cause false failures around interval deadlines. Real failures indicate restart monitor interval misbehavior, paused task mishandling, event publication loss, or incorrect restart count labels.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/restart_monitor_test.go -->
