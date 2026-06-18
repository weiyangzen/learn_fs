# sources/cloud-native/moby/integration-cli/daemon_swarm_hack_test.go

## Purpose
Small compatibility helper for mapping swarm node IDs to daemon helpers in legacy tests.

## Important APIs and Types
Defines `(*DockerSwarmSuite).getDaemon` and `nodeCmd`.

## Control Flow, State, and Persistence
`getDaemon` searches the suite's daemon slice for a daemon whose node ID matches the requested ID and fails the test if absent. `nodeCmd` runs a command against that daemon.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on swarm suite state populated in `check_test.go`. Risks include stale node IDs after daemon restart and test failure diagnostics when nodes are removed. Swarm tests that address nodes by ID validate it.
