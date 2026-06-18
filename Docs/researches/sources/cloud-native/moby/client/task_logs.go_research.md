# sources/cloud-native/moby/client/task_logs.go

## Purpose
Implements streaming log retrieval for a single swarm task.

## APIs, Types, And Functions
`TaskLogsOptions` mirrors service log flags; `TaskLogsResult` is an `io.ReadCloser`; `Client.TaskLogs` sends `GET /tasks/{id}/logs` and wraps the response in `newCancelReadCloser`.

## Control Flow, State, And Integration
The method builds stdout/stderr, since, timestamps, details, follow, and tail query values, parses `Since`, sends the GET request, and returns a cancel-aware stream. Unlike service logs, it always sets `tail` from the option value.

## Risks And Test Signals
Risks include missing task ID validation, inconsistent `Until` handling despite the option field, stream leaks, and log query drift relative to service/container logs. Integration is with daemon task log endpoints and live log consumers.
