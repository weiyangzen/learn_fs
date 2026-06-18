# sources/cloud-native/moby/integration/internal/swarm/states.go

Purpose: polling predicates for swarm task and node states.

Important APIs and helpers: `NoTasksForService`, `NoTasks`, `RunningTasksCount`, `JobComplete`, and `HasLeader`.

Control flow: task predicates call `TaskList` with relevant filters, inspect desired/current states, and return poll success or continue. `JobComplete` handles replicated-job and global-job modes by counting completed tasks against service replicas or node count, while continuing on pending/running tasks and erroring on failed tasks. `HasLeader` lists manager nodes and succeeds when a reachable leader is present.

State and persistence: reads swarm task/service/node state but does not mutate it. It interprets orchestrator convergence and job completion.

Dependencies and integration: depends on swarm API types, client task/node APIs, filters, errdefs, and gotest poll.

Risks: swarm state is eventually consistent; predicates must be used with suitable timeouts. `JobComplete` errors on any failed task, which is correct for tests expecting successful jobs but not for negative-job tests.

Test signals: helper-only; provides high-level readiness/completion checks for swarm integration tests.
