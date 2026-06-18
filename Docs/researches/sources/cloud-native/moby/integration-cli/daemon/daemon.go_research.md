# sources/cloud-native/moby/integration-cli/daemon/daemon.go

## Purpose
Legacy integration helper wrapper around `internal/test/daemon.Daemon`.

## Important APIs and Types
Defines `Daemon` embedding the newer daemon helper and methods `New`, `Cmd`, `RunCmd`, `Command`, `PrependHostArg`, `GetIDByName`, `InspectField`, `CheckActiveContainerCount`, `WaitRun`, and `WaitInspectWithArgs`.

## Control Flow, State, and Persistence
The wrapper constructs daemon-bound CLI commands, prepends `-H` host arguments, runs inspect filters, checks active container counts, and polls for running/exited states. It delegates daemon lifecycle to the embedded helper.

## Dependencies, Integration Points, Risks, and Test Signals
Used by daemon/swarm/plugin suites to target specific daemon instances. Depends on CLI binary paths, `icmd`, and inspect formatting. Risks include host-arg ordering, polling timeouts, and stale container counts across tests. Swarm and daemon integration tests provide signals.
