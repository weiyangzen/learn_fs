# sources/cloud-native/moby/integration-cli/docker_api_swarm_node_test.go

Purpose: tests Swarm node API behavior for listing nodes, updating node availability, force-removing nodes, and scheduler reactions to drain and pause availability states.

Important APIs, types, and functions: `TestAPISwarmListNodes`, `TestAPISwarmNodeUpdate`, `TestAPISwarmNodeRemove`, and `TestAPISwarmNodeDrainPause`. It uses `DockerSwarmSuite.AddDaemon`, `daemon.Daemon.ListNodes`, `UpdateNode`, `GetNode`, `RemoveNode`, `RestartNode`, `SwarmInfo`, `CreateService`, `UpdateService`, `CheckActiveContainerCount`, `ActiveContainers`, and shared service helpers `simpleTestService` and `setInstances`.

Control flow: tests build small clusters, inspect returned node IDs against daemon node IDs, mutate `swarm.Node.Spec.Availability`, and poll until scheduler state converges. Drain/pause creates a replicated service over two nodes, drains one node and verifies tasks move, reactivates and resizes the service, then pauses the node and verifies scale-up places only new tasks on the active node.

State and persistence behavior: mutates real swarm cluster state: node membership, node availability, service desired replica count, and task/container placement. `TestAPISwarmNodeRemove` verifies removed node membership is not restored by restarting the daemon. Polling is required because raft replication and scheduler reconciliation are asynchronous.

Dependencies and integration points: `!windows` build-tagged. Uses Moby swarm API types, integration daemon helpers, custom checkers, `poll.WaitOn`, and network availability for force removal. Depends on helper functions and default timeout from `docker_api_swarm_test.go`.

Risks and edge cases: node restart after removal uses a fixed one-second wait, which can be brittle on slow CI. Drain/pause assertions depend on scheduler balancing and may be sensitive to image pull/startup delays. The file assumes the shared service helper creates long-running BusyBox `top` tasks.

Test signals: validates node list completeness, node availability update persistence, force removal preventing rejoin after restart, drain rescheduling all tasks away from a node, reactivation allowing future task placement, and pause preserving existing tasks while blocking new task assignments.
