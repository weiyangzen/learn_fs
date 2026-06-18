# Research: sources/cloud-native/nydus-snapshotter/pkg/manager/daemon_event.go

This file handles daemon liveness events, restart/failover recovery, and hot upgrade. `SubscribeDaemonEvent` and `UnsubscribeDaemonEvent` wrap the liveness monitor. `handleDaemonDeathEvent` consumes death notifications, records daemon count decrement, resets cached state, and dispatches according to recover policy.

`doDaemonRestart` waits for the old process, unsubscribes, clears vestiges, restarts the daemon, and remounts shared RAFS instances. `doDaemonFailover` waits, unsubscribes, asks supervisor to send states, restarts the daemon, waits for `INIT`, calls `TakeOver`, then starts service. `DoDaemonUpgrade` clones daemon state and RAFS instances, chooses the next API socket name, starts a new daemon with `--upgrade`, transfers states, waits through `INIT` and `READY`, unsubscribes the old daemon, asks it to exit, starts the new daemon, subscribes it, waits for `RUNNING`, recovers mounts, and persists the new daemon. `buildNextAPISocket` increments `apiN.sock`.

State spans supervisor sockets, daemon process IDs, API sockets, RAFS cache, monitor subscriptions, and manager store. Risks include asynchronous recovery races, upgrade rollback gaps, socket-name assumptions, supervisor nil assumptions in failover, and limited unit tests for helper behavior in this subset.
