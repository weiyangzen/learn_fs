# sources/cloud-native/moby/integration/container/restart_test.go

Purpose: Restart behavior tests for daemon restart/live-restore interactions, health monitor recovery, auto-remove restart semantics, and client-request cancellation.

Important APIs and flow: `TestDaemonRestartKillContainers` runs matrix cases over live-restore on/off and daemon kill/stop, with containers that may have restart policies and healthchecks. It restarts dockerd and verifies running state and new healthchecks. `pollForNewHealthCheck` checks health log timestamps. `TestContainerWithAutoRemoveCanBeRestarted` restarts `--rm` containers and ensures removal only after kill/stop. `TestContainerRestartWithCancelledRequest` cancels a timed restart request, listens for a restart event, and verifies the container is running.

State and dependencies: Uses child daemons, event streams, restart policies, health files, and auto-remove metadata. Windows has retry accommodation for signal timing.

Risks and signals: It catches daemon lifecycle regressions where restart requests are aborted by client cancellation, health monitors are not restored, or auto-remove containers are removed too early.
