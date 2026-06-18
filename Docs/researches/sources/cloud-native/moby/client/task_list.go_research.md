# sources/cloud-native/moby/client/task_list.go

## Purpose
Implements listing swarm tasks with optional filter query parameters.

## APIs, Types, And Functions
`TaskListOptions` contains `Filters`; `TaskListResult` contains `[]swarm.Task`; `Client.TaskList` performs the list request. It depends on filter URL encoding and JSON decoding.

## Control Flow, State, And Integration
The method applies filters to query values, calls `GET /tasks`, decodes the response array, and closes the body. It reads daemon scheduler state and persists nothing locally.

## Risks And Test Signals
Risks include filter encoding bugs and schema drift in `swarm.Task`. Integration points are service/task status views and swarm scheduling diagnostics.
