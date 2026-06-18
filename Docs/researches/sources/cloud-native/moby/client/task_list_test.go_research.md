# sources/cloud-native/moby/client/task_list_test.go

## Purpose
Tests task list daemon error handling and successful task array decoding.

## APIs, Types, And Functions
`TestTaskListError` and `TestTaskList` call `Client.TaskList`, pass `TaskListOptions`, use mock `GET /tasks`, and compare `swarm.Task` results.

## Control Flow, State, And Integration
The mock server returns a failure for the error path and a JSON array for the success path. Tests assert method/path correctness and decoded task IDs.

## Risks And Test Signals
The file catches endpoint and decode regressions. Filter query coverage is limited, leaving filter-specific behavior dependent on shared filter helpers.
