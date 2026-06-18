# sources/cloud-native/moby/integration/container/daemon_test.go

Purpose: Cross-file daemon restart tests for cleanup after unclean daemon termination, focused on killing stuck containers and clearing stale network state.

Important APIs and flow: `TestContainerKillOnDaemonStart` starts an isolated daemon, runs a long-lived container, kills dockerd, restarts it, and checks the container is no longer running. `TestNetworkStateCleanupOnDaemonStart` adds exposed port bindings, verifies `SandboxID`, `SandboxKey`, and port mappings exist, kills dockerd, restarts, and verifies those network settings are cleared. It uses `daemon.New`, `container.Run`, `ContainerInspect`, `ContainerRemove`, and `network.MustParsePort`.

State and dependencies: The tests persist container metadata across daemon death and restart, then assert daemon startup reconciliation. They require a local, non-Windows, non-rootless daemon because they manage dockerd directly and inspect host-side network cleanup behavior.

Risks and signals: They detect stale runtime/network state after daemon crash or live-restore-like conditions. Failures can leave containers incorrectly marked running or port/network settings still attached after runtime state is gone.
