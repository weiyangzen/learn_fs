<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/docker_windows.go -->
# sources/cloud-native/moby/daemon/command/docker_windows.go

## Purpose
Adds Windows service handling and ETW logging setup around daemon command execution.

## Important APIs, Types, And Functions
`runDaemon` calls `initService`, may clear `Pidfile`, starts `cli.start`, and calls `notifyShutdown`. `initLogging` writes logs to stdout and adds an ETW hook.

## Control Flow
Service registration/unregistration can short-circuit startup. Running as SCM service changes pidfile behavior and routes shutdown status back to service code.

## State And Persistence Behavior
Mutates global logger output/hooks and may clear daemon pidfile config while under service management. ETW hook persists for process lifetime.

## Dependencies And Integration Points
Integrates `service_windows.go`, Microsoft winio ETW logrus hook, containerd logging, and platform `daemonCLI` lifecycle.

## Risks And Test Signals
Risks include swallowed ETW hook setup errors, divergent stdout/stderr behavior from Unix, and service mode suppressing pidfiles. Windows service paths are the primary integration signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/docker_windows.go -->
