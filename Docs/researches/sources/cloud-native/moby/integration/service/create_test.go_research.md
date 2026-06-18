# sources/cloud-native/moby/integration/service/create_test.go

## Purpose
Exercises Docker Swarm service creation paths against real daemons. The file validates service `Init`, repeated create/remove cycles, name conflict handling, max replica scheduling, secret/config file modes, sysctl and capability propagation, and resource knobs for memory swap and memory swappiness.

## Important APIs, Types, And Functions
- `TestServiceCreateInit` and `testServiceCreateInit` start swarms with and without `daemon.WithInit()` and compare generated task container `HostConfig.Init`.
- `inspectServiceContainer` locates the one task container by `com.docker.swarm.service.id` label and returns a `container.InspectResponse`.
- `TestCreateServiceMultipleTimes`, `TestCreateServiceConflict`, and `TestCreateServiceMaxReplicas` cover basic service lifecycle invariants.
- `TestCreateServiceSecretFileMode` and `TestCreateServiceConfigFileMode` create Swarm secrets/configs, mount them into a service, and read service logs for Unix mode bits.
- `TestCreateServiceSysctls`, `TestCreateServiceCapabilities`, `TestCreateServiceMemorySwap`, and `TestCreateServiceMemorySwappiness` inspect service specs, task specs, and task containers for plumbed options.

## Control Flow
Each test calls `setupTest`, starts an isolated Swarm daemon with `swarm.NewSwarm`, creates API clients, creates services through integration helpers or direct client calls, waits for convergence with `poll.WaitOn`, then inspects service/task/container state. Resource tests iterate table cases and reuse the same daemon. Secret/config tests explicitly remove services, wait for task removal, and remove the created secret/config.

## State And Persistence
State is held in the test daemon's Swarm raft state, overlay networks, services, tasks, secrets, configs, and task containers. Daemons are stopped with `defer d.Stop(t)`, and the package cleanup path removes non-protected resources after each test. `TestCreateServiceMultipleTimes` deliberately checks that after service removal and task deallocation, an overlay network can be removed without lingering task references.

## Dependencies And Integration Points
Depends on Moby's client APIs, Swarm integration helpers, network helpers, `testutil.StartSpan`, `daemon` options, `gotest.tools` assertions, and `poll`. The tests integrate with SwarmKit scheduling, service controller updates, container creation, secret/config materialization, cgroup/resource host config translation, and daemon environment flags such as swap support.

## Risks And Edge Cases
Many tests are skipped on Windows; several assume Linux-specific file modes and Swarm behavior. Task convergence and network removal are asynchronous, so polling and retry loops are required. The memory swap container assertion is conditional on daemon swap-limit support, while memory swappiness is only asserted at service/task spec level because host support can silently clear container host config fields.

## Test Signals
Strong signals include one running task per service, expected service conflict errors, service and task specs matching requested sysctls/capabilities/resources, secret/config `ls -l` output containing requested modes, and task container `HostConfig` reflecting the service-level options where the daemon supports them.
