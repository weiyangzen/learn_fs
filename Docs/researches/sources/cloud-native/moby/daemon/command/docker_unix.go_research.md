<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/docker_unix.go -->
# sources/cloud-native/moby/daemon/command/docker_unix.go

## Purpose
Supplies Unix-specific daemon command run and logging wiring.

## Important APIs, Types, And Functions
`runDaemon` calls `cli.start`; `initLogging` directs containerd log output to stderr.

## Control Flow
There is no extra wrapper behavior on Unix: the daemon CLI starts directly under the provided context.

## State And Persistence Behavior
Only global logger output is mutated. The file performs no disk or daemon state changes by itself.

## Dependencies And Integration Points
Used by `NewDaemonRunner` in `docker.go` and the platform build tags. Depends on `github.com/containerd/log`.

## Risks And Test Signals
Risk is mainly stream routing regressions for daemon logs. Integration coverage comes from command startup tests and CLI execution paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/docker_unix.go -->
