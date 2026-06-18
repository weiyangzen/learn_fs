<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_windows.go -->
# sources/cloud-native/moby/daemon/command/daemon_windows.go

## Purpose
Implements Windows-specific daemon command hooks for config defaults, service readiness, shutdown notification, reload signaling, swarm roots, port allocation no-op behavior, and containerd startup decisions.

## Important APIs, Types, And Functions
`getDefaultDaemonConfigFile`, `setPlatformOptions`, `preNotifyReady`, `notifyShutdown`, `daemonCLI.setupConfigReloadTrap`, `getSwarmRunRoot`, `allocateDaemonPort`, `newCgroupParent`, `daemonCLI.initContainerd`, and `validateCPURealtimeOptions`.

## Control Flow
Windows defers the pidfile location until `Root` is known. Service startup is acknowledged before the daemon is fully ready. Reload is driven by a named global Win32 event watched in a goroutine. Containerd is initialized only when a non-legacy runtime needs it.

## State And Persistence Behavior
May set `cfg.Pidfile` under the data root and interacts with global Windows service state. Reload event names include the process ID.

## Dependencies And Integration Points
Integrates with `golang.org/x/sys/windows`, containerd log output, Windows service code in `service_windows.go`, and daemon config runtime names.

## Risks And Test Signals
Risks include service timeout ordering, reload event handle errors being ignored, and incorrect runtime gating around legacy HCS runtime. Windows service and config tests provide coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_windows.go -->
