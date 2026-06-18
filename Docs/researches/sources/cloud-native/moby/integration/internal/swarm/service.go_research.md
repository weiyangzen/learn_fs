# sources/cloud-native/moby/integration/internal/swarm/service.go

Purpose: shared helpers for starting swarm-mode daemons, creating service specs/services, polling, and executing commands in service tasks.

Important APIs and helpers: `ServicePoll`, `NetworkPoll`, `NewSwarm`, `ServiceSpecOpt`, `CreateService`, `CreateServiceSpec`, `ServiceWithMode`, `ServiceWithInit`, `ServiceWithImage`, `ServiceWithCommand`, `ServiceWithConfig`, `ServiceWithSecret`, `ServiceWithReplicas`, `ServiceWithMaxReplicas`, `ServiceWithPlacementConstraints`, `ServiceWithName`, `ServiceWithNetwork`, `ServiceWithEndpoint`, `ServiceWithSysctls`, `ServiceWithCapabilities`, `ServiceWithPidsLimit`, `ServiceWithMemorySwap`, `ServiceWithMemorySwappiness`, `GetRunningTasks`, `ExecTask`, and resource-initialization helpers.

Control flow: `NewSwarm` starts a daemon with busybox, creates a client, and initializes swarm. Spec options ensure nested task/container/resources/placement fields exist before mutation. `CreateService` builds a spec and calls `ServiceCreate`. `GetRunningTasks` lists tasks filtered by service and running state. `ExecTask` finds the container ID from a task status, creates an exec, attaches it, and starts it.

State and persistence: creates a real daemon in swarm mode, swarm services, tasks, networks, configs/secrets references, and exec sessions. Spec helpers mutate in-memory service specs.

Dependencies and integration: depends on swarm API types, daemon harness, environment execution, client service/task/node APIs, poll settings, and container exec APIs.

Risks: helpers assert/fail directly and are not suited for expected-error tests. Swarm convergence is asynchronous, so callers must combine service creation with polling predicates from `states.go`.

Test signals: helper-only; centralizes service creation and task interaction for swarm integration tests.
