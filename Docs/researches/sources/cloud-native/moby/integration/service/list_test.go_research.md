# sources/cloud-native/moby/integration/service/list_test.go

## Purpose
Ensures `ServiceList` honors the `Status` option: default list responses omit service status, while `Status: true` includes desired and running task counts matched to each service.

## Important APIs, Types, And Functions
- `TestServiceListWithStatuses` creates three replicated services using `fullSwarmServiceSpec`.
- Inline polling uses `TaskList` filtered by service ID and counts tasks in `TaskStateRunning`.
- `ServiceListOptions{Status: true}` is the API feature under test.

## Control Flow
The test starts Swarm, creates three services with 1, 2, and 3 replicas, waits for each service's running tasks, lists services without status and checks nil `ServiceStatus`, then lists with status and checks desired/running counts equal each service's replica count.

## State And Persistence
Service and task state persists in the test Swarm until cleanup. No local files are written.

## Dependencies And Integration Points
Integrates Moby API service list handling with SwarmKit status aggregation. Reuses the inspect test's full spec helper and Moby client filters.

## Risks And Edge Cases
The test intentionally avoids unconverged service status assertions because reliably inducing and observing partial convergence is difficult. It assumes all created services are the only services visible in the isolated daemon.

## Test Signals
Passing means `ServiceStatus` is absent by default and present with correct `DesiredTasks` and `RunningTasks` when requested.
