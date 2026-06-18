# sources/cloud-native/moby/integration-cli/check_test.go

## Purpose
Legacy integration-cli test harness that registers suites, prepares the test environment, and defines suite-level setup/teardown behavior.

## Important APIs and Types
Defines `TestMain`, `testRun`, suite entry tests for API/CLI/registry/daemon/swarm/plugin/network/hub suites, and suite structs including `DockerSuite`, registry auth suites, `DockerDaemonSuite`, `DockerSwarmSuite`, and `DockerPluginSuite`.

## Control Flow, State, and Persistence
`TestMain` initializes execution environment, prints versions, and runs all suite wrappers. Suite setup starts registries, daemons, swarm nodes, and plugin fixtures as needed. Teardown removes containers, networks, volumes, daemons, registries, and plugin state.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on `internal/test/environment`, integration helpers, registry fixtures, daemon helpers, and Docker CLI/API binaries. It is the central integration point for legacy tests. Risks include global mutable `testEnv`, cleanup gaps causing cross-test pollution, and deprecated suite expansion. Its test wrappers provide broad behavioral signals across the daemon.
