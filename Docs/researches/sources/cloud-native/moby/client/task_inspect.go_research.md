# sources/cloud-native/moby/client/task_inspect.go

## Purpose
Implements inspection of a single swarm task through the Docker API client.

## APIs, Types, And Functions
`TaskInspectOptions` is empty; `TaskInspectResult` wraps `swarm.Task`; `Client.TaskInspect` validates the task ID and decodes the daemon response.

## Control Flow, State, And Integration
The method trims the task ID, calls `GET /tasks/{id}`, decodes JSON into a task object, and closes the response reader. It reads scheduler task state without mutating local or daemon state.

## Risks And Test Signals
Risks include empty ID handling, endpoint path drift, and swarm task schema evolution. Integration is with swarm scheduler state, service diagnostics, and task-level log/status workflows.
