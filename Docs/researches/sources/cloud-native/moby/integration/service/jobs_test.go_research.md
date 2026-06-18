# sources/cloud-native/moby/integration/service/jobs_test.go

## Purpose
Tests Swarm job service modes: creating replicated and global jobs, running a replicated job to completion, and updating a completed replicated job to start a new job iteration.

## Important APIs, Types, And Functions
- `TestCreateJob` creates services with `ReplicatedJob` and `GlobalJob` modes and waits for one running task.
- `TestReplicatedJob` sets `MaxConcurrent` and `TotalCompletions`, uses command `true`, and waits for `swarm.JobComplete`.
- `TestUpdateReplicatedJob` increments `TaskTemplate.ForceUpdate`, updates the service, checks `JobIteration` increases, and waits for the second completion.

## Control Flow
All tests skip remote daemons and Windows, create an isolated Swarm, create job-mode services, then rely on polling to observe running tasks or completed job status. The update path inspects the service before and after `ServiceUpdate`.

## State And Persistence
Job state lives in Swarm service `Mode`, `JobStatus`, service versions, and task history. Completed job tasks remain part of Swarm history until daemon cleanup.

## Dependencies And Integration Points
Uses Swarm service APIs, `swarm.CreateService`, `swarm.JobComplete`, `client.ServiceUpdate`, and SwarmKit job orchestration. The tests integrate with scheduler completion accounting and job iteration versioning.

## Risks And Edge Cases
The replicated job deliberately keeps total completions low because CI startup overhead can make higher totals time out. Polling must distinguish a completed job from transient task creation. Behavior is Linux/local-daemon oriented.

## Test Signals
Successful signals are running tasks for job services, `JobComplete` success for command `true`, and a strictly increasing `JobStatus.JobIteration.Index` after a forced update.
